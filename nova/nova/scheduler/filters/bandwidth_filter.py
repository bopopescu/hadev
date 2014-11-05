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


class BandwidthFilter(filters.BaseHostFilter):
    """Disk Filter with over subscription flag."""

    def host_passes(self, host_state, filter_properties):
        """Filter based on disk usage."""
        instance_type = filter_properties.get('instance_type')
        if instance_type.get('network_bandwidth') != None:
            requested_bandwidth = instance_type['network_bandwidth'];
        else:
            requested_bandwidth = 100;



        available_bandwidth = host_state.total_bandwidth - host_state.used_bandwidth;
        available_bandwidth = 1000;
        if requested_bandwidth > available_bandwidth:
            return False

        return True


