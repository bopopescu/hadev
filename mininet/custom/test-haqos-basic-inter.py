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
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import requests
import threading





def createTopo(  ):
    "Simple topology example."


    net = Mininet( controller=RemoteController)
    params = {'ip':'127.0.0.1','port':6633}
    info( '*** Adding controller\n' )
    net.addController( 'c0', controller=RemoteController, **params)

    # Add hosts and switches
    host1 = net.addHost( 'h1' )
    host2 = net.addHost( 'h2' )
    host3 = net.addHost( 'h3' )
    host4 = net.addHost( 'h4' )
    leftSwitch = net.addSwitch( 's5' )
    rightSwitch = net.addSwitch( 's6' )
    centerSwitchl = net.addSwitch( 's7' )
    centerSwitchr = net.addSwitch( 's8' )

    # Add links
    linkOpts = {'bw':100};
    net.addLink( host1, leftSwitch ) #, cls=TCLink, **linkOpts)
    net.addLink( host2, leftSwitch ) #, cls=TCLink, **linkOpts)
    linkOpts = {'bw':100};
    net.addLink( leftSwitch, centerSwitchl ) #, cls=TCLink, **linkOpts)
    net.addLink( centerSwitchl, centerSwitchr) # , cls=TCLink, **linkOpts)
    net.addLink( centerSwitchr, rightSwitch) # , cls=TCLink, **linkOpts)

    linkOpts = {'bw':100};
    net.addLink( rightSwitch, host3) #, cls=TCLink, **linkOpts)
    net.addLink( rightSwitch, host4) #, cls=TCLink, **linkOpts)
    

    info( '*** Starting network\n')
    net.start()
    net.pingAll();
    time.sleep(5);

    info( '*** adding q h1-h2\n' )
    cmd1 = 'curl -i http://221.199.216.240:8080/wm/haqos/reserveInterBw/00:00:00:00:00:00:00:05/00:00:00:00:00:00:00:06/20000000/5001/10.0.0.1/json -X PUT';
    result1 = os.popen(cmd1);
    time.sleep(3);
    info( '*** adding q h2-h1\n' )
    cmd2 = 'curl -i http://221.199.216.240:8080/wm/haqos/reserveInterBw/00:00:00:00:00:00:00:06/00:00:00:00:00:00:00:05/20000000/-1/10.0.0.3/json -X PUT';
    result2 = os.popen(cmd2);


    time.sleep(5);


    info( '*** Running CLI\n' )
    CLI( net )



    info( '*** Stopping network' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    createTopo()


