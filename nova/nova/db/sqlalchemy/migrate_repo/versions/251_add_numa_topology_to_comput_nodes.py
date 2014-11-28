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


from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy import Integer


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    compute_nodes = Table('compute_nodes', meta, autoload=True)
    shadow_compute_nodes = Table('shadow_compute_nodes', meta, autoload=True)
    instances = Table('instances', meta, autoload=True)

    numa_topology = Column('numa_topology', Text, nullable=True)
    shadow_numa_topology = Column('numa_topology', Text, nullable=True)
    total_bandwidth = Column('total_bandwidth', Integer, nullable=True)
    bandwidth_used = Column('bandwidth_used', Integer, nullable=True)
    network_bandwidth = Column('network_bandwidth', Integer, nullable=True)
    disk_gb_used = Column('disk_gb_used', Integer, nullable=True)
    ram_mb_used = Column('ram_mb_used', Integer, nullable=True)
    used_bandwidth = Column('used_bandwidth', Integer, nullable=True)

    compute_nodes.create_column(numa_topology)
    compute_nodes.create_column(total_bandwidth)
    compute_nodes.create_column(bandwidth_used)

    shadow_compute_nodes.create_column(shadow_numa_topology)

    instances.create_column(network_bandwidth)
    instances.create_column(disk_gb_used)
    instances.create_column(ram_mb_used)
    instances.create_column(used_bandwidth)

def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    compute_nodes = Table('compute_nodes', meta, autoload=True)
    shadow_compute_nodes = Table('shadow_compute_nodes', meta, autoload=True)
    instances = Table('instances', meta, autoload=True)

    compute_nodes.drop_column('numa_topology')
    compute_nodes.drop_column('total_bandwidth')
    compute_nodes.drop_column('bandwidth_used')

    shadow_compute_nodes.drop_column('numa_topology')

    instances.drop_column('network_bandwidth');
    instances.drop_column('disk_gb_used');
    instances.drop_column('ram_mb_used');
    instances.drop_column('used_bandwidth');
