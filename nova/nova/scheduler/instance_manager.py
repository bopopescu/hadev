# Copyright (c) 2011 OpenStack Foundation
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

"""
Manage hosts in the current zone.
"""

import collections
import UserDict

from oslo.config import cfg

from nova.compute import task_states
from nova.compute import vm_states
from nova import db
from nova import exception
from nova.i18n import _, _LW
from nova.openstack.common import jsonutils
from nova.openstack.common import log as logging
from nova.openstack.common import timeutils
from nova.pci import pci_stats
from nova.scheduler import filters
from nova.scheduler import weights
from nova.virt import hardware
from nova import notifications


instance_manager_opts = [
    cfg.MultiStrOpt('scheduler_avail_inst_filters',
            default=['nova.scheduler.filters.all_instance_filters'],
            help='Filter classes available to the scheduler which may '
                    'be specified more than once.  An entry of '
                    '"nova.scheduler.filters.standard_filters" '
                    'maps to all filters included with nova.'),
    cfg.ListOpt('scheduler_instance_filters',
                default=[
                  'InstanceFilter',
                  ],
                help='Which filter class names to use for filtering instances '
                      'when not specified in the request.'),
    ]

CONF = cfg.CONF
CONF.register_opts(instance_manager_opts)

LOG = logging.getLogger(__name__)


class InstanceState(object):
    """Mutable and immutable information tracked for a host.
    This is an attempt to remove the ad-hoc data structures
    previously used and lock down access.
    """

    def __init__(self, instance):

        # Mutable available resources.
        # These will change as resources are virtually "consumed".
        self.instance = instance;
        if instance.get('disk_gb_used') == None:
            self.disk_mb_used = 0;
        else:
            self.disk_mb_used = instance['disk_gb_used'] * 1024; 
        if instance.get('ram_mb_used') == None:
            self.ram_mb_used = 0;
        else:
            self.ram_mb_used = instance['ram_mb_used']; 
        self.free_disk_mb = (instance['root_gb'] + instance['ephemeral_gb']) * 1024 - self.disk_mb_used;
        self.free_ram_mb = instance['memory_mb'] - self.ram_mb_used;
        #self.vcpus_used = 0

        self.num_apps = 0

        # Bandwidth Information.
        self.total_bandwidth = instance['network_bandwidth'];
        if instance.get('used_bandwidth') == None:
            self.used_bandwidth = 0;
        else:
            self.used_bandwidth = instance['used_bandwidth'];




    def consume_from_app(self, context, app):
        bandwidth = app['network_bandwidth']

        self.free_ram_mb -= app['memory_mb']
        self.free_disk_mb -= app['disk_gb']*1024
        #self.vcpus_used += app['vcpus']
        self.updated = timeutils.utcnow()
        self.used_bandwidth += bandwidth;
        self.num_apps += 1;


        update_dict = {};
        update_dict['disk_gb_used'] = float(self.free_disk_mb)/1024.0;
        update_dict['ram_mb_used'] = self.free_ram_mb;
        update_dict['used_bandwidth'] = self.used_bandwidth;

        instance_uuid = self.instance['uuid'];
        
        (old_ref, new_ref) = db.instance_update_and_get_original(context,
                instance_uuid, update_dict);

        notifications.send_update(context, old_ref, new_ref,
                                  service="scheduler")



class InstanceManager(object):
    """Base HostManager class."""

    # Can be overridden in a subclass
    def instance_state_cls(self, instance, **kwargs):
        return InstanceState(instance, **kwargs)

    def __init__(self):
        self.instance_state_map = {}
        self.filter_handler = filters.InstanceFilterHandler()
        self.filter_classes = self.filter_handler.get_matching_classes(
                CONF.scheduler_avail_inst_filters)

    def _choose_instance_filters(self, filter_cls_names):
        """Since the caller may specify which filters to use we need
        to have an authoritative list of what is permissible. This
        function checks the filter names against a predefined set
        of acceptable filters.
        """
        if filter_cls_names is None:
            filter_cls_names = CONF.scheduler_instance_filters
        if not isinstance(filter_cls_names, (list, tuple)):
            filter_cls_names = [filter_cls_names]
        cls_map = dict((cls.__name__, cls) for cls in self.filter_classes)
        good_filters = []
        bad_filters = []
        for filter_name in filter_cls_names:
            if filter_name not in cls_map:
                bad_filters.append(filter_name)
                continue
            good_filters.append(cls_map[filter_name])
        if bad_filters:
            msg = ", ".join(bad_filters)
            raise exception.SchedulerHostFilterNotFound(filter_name=msg)
        return good_filters

    def get_filtered_instances(self, instances, filter_properties,
            filter_class_names=None, index=0):
        """Filter instances and return only ones passing all filters."""

        filter_classes = self._choose_instance_filters(filter_class_names)

        return self.filter_handler.get_filtered_objects(filter_classes,
                instances, filter_properties, index)

    def get_all_instances(self, context, instance_uuid=None):
        """Returns a list of HostStates that represents all the hosts
        the HostManager knows about. Also, each of the consumable resources
        in HostState are pre-populated and adjusted based on data in the db.
        """

        # Get resource usage across the available compute nodes:
        instances = db.instance_get_all(context)
        instance_states = [];
        if instance_uuid == None:
            LOG.info(_("None instance_uuid"));

        for instance in instances:
            vm_state = instance.get('vm_state')

            if vm_state == None or vm_state != vm_states.ACTIVE:
                continue;
            if instance_uuid != None and instance['uuid'] == instance_uuid:
                LOG.info(_("found matching uuid instance"));
                continue;

            instance_state = self.instance_state_cls(instance);
            instance_states.append(instance_state);

        return instance_states;
