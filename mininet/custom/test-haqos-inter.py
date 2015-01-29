"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

import os
import sys
import time
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def createDatacenter( ):

    net = Mininet( controller=RemoteController)

    info( '*** Adding controller\n' )
    net.addController( 'c0', controller=RemoteController,ip="127.0.0.1",port=6633 )

    # Build 16 hosts 
    hosts = [];
    i = 0;
    while (i < 24):
        hosts.append(net.addHost('h%s' % (i+1)));
        i += 1;

    # Build 2 Core switches
    core = [];
    j = 0;
    while (j < 2):
        core.append(net.addSwitch('s%s' % (i+1)));
        i += 1;
        j += 1;

    # Build 4 Aggr switches
    aggr = [];
    j = 0;
    while (j < 4):
        aggr.append(net.addSwitch('s%s' % (i+1)));
        i += 1;
        j += 1;

    # Build 8 Edge switches
    edge = [];
    j = 0;
    while (j < 8):
        edge.append(net.addSwitch('s%s' % (i+1)));
        i += 1;
        j += 1;


    # Link aggr with core 
    i = 0;
    linkOpts = {'bw':100};
    while (i < 4):
        j = 0;
        while j < 2:
            net.addLink (aggr[i], core[j]) #, cls=TCLink, **linkOpts);
            j += 1;
        i += 1;

    # Link edge with aggr
    i = 0;
    linkOpts = {'bw':50};
    while (i < 8):
        j = i / 2;
        net.addLink (edge[i], aggr[j]) #, cls=TCLink, **linkOpts);
        i += 1;

    # Link host with edge
    i = 0;
    linkOpts = {'bw':20};
    while (i < 24):
        j = i / 3;
        net.addLink (hosts[i], edge[j]) #, cls=TCLink, **linkOpts);
        i += 1;


    info( '*** Starting network\n')
    net.start()


    time.sleep(15);


    info( '*** adding q h1-h2\n' )
    cmd1 = 'curl -i http://221.199.216.240:8080/wm/haqos/reserveInterBw/00:00:00:00:00:00:00:1f/s31-eth2/00:00:00:00:00:00:00:26/s38-eth2/30000000/5001/10.0.0.1/json -X PUT';
    result1 = os.popen(cmd1);
    time.sleep(3);
    info( '*** adding q h2-h1\n' )
    cmd2 = 'curl -i http://221.199.216.240:8080/wm/haqos/reserveInterBw/00:00:00:00:00:00:00:26/s38-eth2/00:00:00:00:00:00:00:1f/s31-eth2/30000000/-1/10.0.0.22/json -X PUT';
    result2 = os.popen(cmd2);


    info( '*** adding q h1-h2\n' )
    cmd1 = 'curl -i http://221.199.216.240:8080/wm/haqos/reserveInterBw/00:00:00:00:00:00:00:1f/s31-eth3/00:00:00:00:00:00:00:26/s38-eth3/30000000/5001/10.0.0.2/json -X PUT';
    result1 = os.popen(cmd1);
    time.sleep(3);
    info( '*** adding q h2-h1\n' )
    cmd2 = 'curl -i http://221.199.216.240:8080/wm/haqos/reserveInterBw/00:00:00:00:00:00:00:26/s38-eth3/00:00:00:00:00:00:00:1f/s31-eth3/30000000/-1/10.0.0.23/json -X PUT';
    result2 = os.popen(cmd2);


    info( '*** adding q h1-h2\n' )
    cmd1 = 'curl -i http://221.199.216.240:8080/wm/haqos/reserveInterBw/00:00:00:00:00:00:00:1f/s31-eth4/00:00:00:00:00:00:00:26/s38-eth4/30000000/5001/10.0.0.3/json -X PUT';
    result1 = os.popen(cmd1);
    time.sleep(3);
    info( '*** adding q h2-h1\n' )
    cmd2 = 'curl -i http://221.199.216.240:8080/wm/haqos/reserveInterBw/00:00:00:00:00:00:00:26/s38-eth4/00:00:00:00:00:00:00:1f/s31-eth4/30000000/-1/10.0.0.24/json -X PUT';
    result2 = os.popen(cmd2);

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    createDatacenter()
