# Copyright (c) 2012 OpenStack Foundation
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

from oslo.config import cfg

from nova.i18n import _,_LW
from nova.openstack.common import log as logging
from nova.scheduler import filters
from nova.scheduler.filters import utils

LOG = logging.getLogger(__name__)


class InstanceFilter(filters.BaseInstanceFilter):

    def instance_passes(self, instance, filter_properties):
        """Filter based on cpu, memory and bandwidth."""
        if filter_properties.get('network_bandwidth') != None:
            requested_bandwidth = filter_properties['network_bandwidth'];
        else:
            requested_bandwidth = 100;
            LOG.info(_(" None bandwidth"));
        

        available_bandwidth = instance.total_bandwidth - instance.used_bandwidth;
        if requested_bandwidth > available_bandwidth:
            return False

        if filter_properties.get('memory_mb') != None:
            LOG.info(_(" mmeory spec"));
            requested_memory = filter_properties['memory_mb'];
            if instance.free_ram_mb < requested_memory:
                return False;
 
        if filter_properties.get('disk_gb') != None:
            LOG.info(_(" disk spec"));
            requested_disk = filter_properties['disk_gb'] * 1024;
            if instance.free_disk_mb < requested_disk:
                return False;


        if filter_properties.get('instance_uuid') != None:
            if instance.instance['uuid'] == filter_properties['instance_uuid']:
                return False;

        return True


