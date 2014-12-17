# Copyright 2010 OpenStack Foundation
# Copyright 2011 Piston Cloud Computing, Inc
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import base64
import os
import re

from oslo.config import cfg
from oslo import messaging
from oslo.utils import strutils
from oslo.utils import timeutils
import six
import webob
from webob import exc

from nova.api.openstack import common
from nova.api.openstack.compute import ips
from nova.api.openstack.compute.views import apps as views_apps
from nova.api.openstack import wsgi
from nova.api.openstack import xmlutil
from nova import block_device
from nova import compute
from nova.compute import flavors
from nova import exception
from nova.i18n import _
from nova.i18n import _LW
from nova import objects
from nova.openstack.common import log as logging
from nova.openstack.common import uuidutils
from nova import policy
from nova import utils


app_opts = [
    cfg.BoolOpt('enable_instance_password',
                default=True,
                help='Enables returning of the instance password by the'
                     ' relevant server API calls such as create, rebuild'
                     ' or rescue, If the hypervisor does not support'
                     ' password injection then the password returned will'
                     ' not be correct'),
]
CONF = cfg.CONF
CONF.register_opts(app_opts)
CONF.import_opt('network_api_class', 'nova.network')
CONF.import_opt('reclaim_instance_interval', 'nova.compute.manager')

LOG = logging.getLogger(__name__)

XML_WARNING = False


def make_fault(elem):
    fault = xmlutil.SubTemplateElement(elem, 'fault', selector='fault')
    fault.set('code')
    fault.set('created')
    msg = xmlutil.SubTemplateElement(fault, 'message')
    msg.text = 'message'
    det = xmlutil.SubTemplateElement(fault, 'details')
    det.text = 'details'


def make_app(elem, detailed=False):
    elem.set('name')
    elem.set('id')

    global XML_WARNING
    if not XML_WARNING:
        LOG.warn(_LW('XML support has been deprecated and may be removed '
                     'as early as the Juno release.'))
        XML_WARNING = True

    if detailed:
        elem.set('network_bandwidth')
        elem.set('memory_mb')
        elem.set('disk_gb')

        # Attach image node
        image = xmlutil.SubTemplateElement(elem, 'image', selector='image')
        image.set('id')
        xmlutil.make_links(image, 'links')

        # Attach fault node
        make_fault(elem)

        # Attach metadata node
        elem.append(common.MetadataTemplate())

    xmlutil.make_links(elem, 'links')


app_nsmap = {None: xmlutil.XMLNS_V11, 'atom': xmlutil.XMLNS_ATOM}


class AppTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('app', selector='app')
        make_app(root, detailed=True)
        return xmlutil.MasterTemplate(root, 1, nsmap=app_nsmap)




class CommonDeserializer(wsgi.MetadataXMLDeserializer):
    """Common deserializer to handle xml-formatted server create requests.

    Handles standard server attributes as well as optional metadata
    and personality attributes
    """

    metadata_deserializer = common.MetadataXMLDeserializer()


    def _extract_app(self, server_node):
        """Marshal the bandwidth attribute of a parsed request."""
        app = dict();

        name = self._extract_name(server_node);
        app['name'] = name;

        node = self.find_first_child_named(server_node, "app")
        if node is not None:
            app = node;

        bandwidth = self._extract_bandwidth(server_node);
        app['network_bandwidth'] = bandwidth;

        memory = self._extract_memory(server_node);
        app['memory_mb'] = memory;

        disk = self._extract_disk(server_node);
        app['disk_gb'] = disk;

        return app;

    def _extract_name(self, server_node):
        """Marshal the bandwidth attribute of a parsed request."""
        node = self.find_first_child_named(server_node, "name")
        name = "app-1-";
        if node is not None:
            name = node;

        return name;

    def _extract_bandwidth(self, server_node):
        """Marshal the bandwidth attribute of a parsed request."""
        node = self.find_first_child_named(server_node, "network_bandwidth")
        bandwidth = 100;
        if node is not None:
            bandwidth = node;

        return bandwidth;


    def _extract_memory(self, server_node):
        """Marshal the memory attribute of a parsed request."""
        node = self.find_first_child_named(server_node, "memory_mb")
        memory_mb = 100;
        if node is not None:
            memory_mb = node;

        return memory_mb;


    def _extract_disk(self, server_node):
        """Marshal the disk attribute of a parsed request."""
        node = self.find_first_child_named(server_node, "disk_gb")
        disk_gb = 1;
        if node is not None:
            disk_gb = node;

        return disk_gb;




class CreateDeserializer(CommonDeserializer):
    """Deserializer to handle xml-formatted server create requests.

    Handles standard server attributes as well as optional metadata
    and personality attributes
    """

    def default(self, string):
        """Deserialize an xml-formatted server create request."""
        dom = xmlutil.safe_minidom_parse_string(string)
        app = self._extract_app(dom)
        return {'body': {'app': app}}



class AppsController(wsgi.Controller):
    """The Server API base controller class for the OpenStack API."""

    _view_builder_class = views_apps.ViewBuilder


    def __init__(self, ext_mgr=None, **kwargs):
        super(AppsController, self).__init__(**kwargs)
        self.compute_api = compute.API()
        self.ext_mgr = ext_mgr

    def _check_string_length(self, value, name, max_length=None):
        try:
            if isinstance(value, six.string_types):
                value = value.strip()
            utils.check_string_length(value, name, min_length=1,
                                      max_length=max_length)
        except exception.InvalidInput as e:
            raise exc.HTTPBadRequest(explanation=e.format_message())

    def _validate_server_name(self, value):
        self._check_string_length(value, 'Server name', max_length=255)

    @wsgi.response(202)
    @wsgi.serializers(xml=AppTemplate)
    @wsgi.deserializers(xml=CreateDeserializer)
    def create(self, req, body):

        context = req.environ['nova.context']
        server_dict = body['app']

        name = server_dict['name']
        self._validate_server_name(name)
        name = name.strip()

        if server_dict.get('uuid') != None:
            uuid = server_dict['uuid']
            app = dict();
            app['uuid'] = uuid;
            app['display_name'] = name;

            self.compute_api.failover_app (context, app=app)

            appR = self._view_builder.create(req, app);

            robj = wsgi.ResponseObject(appR);

            return robj;
        else:
            uuid = '';
            network_bandwidth = server_dict.get('network_bandwidth');
            memory_mb = server_dict.get('memory_mb');
            disk_gb = server_dict.get('disk_gb');
            if network_bandwidth == None:
                LOG.info(_("None bandwidth"));
            if memory_mb == None:
                LOG.info(_("None memory"));
            if disk_gb == None:
                LOG.info(_("None disk"));
            app = dict();
            app['network_bandwidth'] = network_bandwidth;
            app['memory_mb'] = memory_mb;
            app['disk_gb'] = disk_gb;
            app['uuid'] = uuidutils.generate_uuid();
            app['display_name'] = name;

            self.compute_api.create_app (context, app=app,
                network_bandwidth=network_bandwidth,
                memory_mb=memory_mb,
                disk_gb=disk_gb);

            appR = self._view_builder.create(req, app);

            robj = wsgi.ResponseObject(appR);

            return robj;







def create_resource():
    return wsgi.Resource(AppsController())
