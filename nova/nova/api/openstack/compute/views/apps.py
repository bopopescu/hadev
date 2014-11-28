# Copyright 2010-2011 OpenStack Foundation
# Copyright 2011 Piston Cloud Computing, Inc.
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

import hashlib

from nova.api.openstack import common
from nova.api.openstack.compute.views import addresses as views_addresses
from nova.api.openstack.compute.views import flavors as views_flavors
from nova.api.openstack.compute.views import images as views_images
from nova.compute import flavors
from nova.i18n import _LW
from nova.objects import base as obj_base
from nova.openstack.common import log as logging
from nova.openstack.common import timeutils
from nova import utils


LOG = logging.getLogger(__name__)


class ViewBuilder(common.ViewBuilder):
    """Model a server API response as a python dictionary."""

    _collection_name = "apps"

    _progress_statuses = (
        "ACTIVE",
        "BUILD",
        "REBUILD",
        "RESIZE",
        "VERIFY_RESIZE",
    )

    _fault_statuses = (
        "ERROR", "DELETED"
    )

    def __init__(self):
        """Initialize view builder."""
        super(ViewBuilder, self).__init__()
        self._address_builder = views_addresses.ViewBuilder()
        self._flavor_builder = views_flavors.ViewBuilder()
        self._image_builder = views_images.ViewBuilder()

    def create(self, request, app):
        """View that should be returned when an instance is created."""
        return {
            "app": {
                "id": app["uuid"],
                "links": self._get_links(request,
                                         app["uuid"],
                                         self._collection_name),
            },
        }

    def basic(self, request, app):
        """Generic, non-detailed view of an instance."""
        return {
            "app": {
                "id": app["uuid"],
                "name": app["display_name"],
                "links": self._get_links(request,
                                         app["uuid"],
                                         self._collection_name),
            },
        }

    def show(self, request, app):
        """Detailed view of a single instance."""
        server = {
            "app": {
                "id": app["uuid"],
                "name": app["display_name"],
                "network_bandwidth": app["network_bandwidth"],
                "links": self._get_links(request,
                                         app["uuid"],
                                         self._collection_name),
            },
        }

        return server




