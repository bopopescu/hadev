"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def createTreeTopo():


    net = Mininet( controller=RemoteController)

    info( '*** Adding controller\n' )
    net.addController( 'c0', controller=RemoteController,ip="127.0.0.1",port=6633 )
    # Add hosts and switches
    host1 = net.addHost( 'h1' )
    host2 = net.addHost( 'h2' )

    edgeSwitch1 = net.addSwitch( 's3' )
    edgeSwitch2 = net.addSwitch( 's4' )
    aggrSwitch1 = net.addSwitch( 's5' )
    aggrSwitch2 = net.addSwitch( 's6' )
    coreSwitch = net.addSwitch( 's7' )

    # Add links
    net.addLink( host1, edgeSwitch1 )
    net.addLink( edgeSwitch1, aggrSwitch1 )
    net.addLink( aggrSwitch1, coreSwitch )
    net.addLink( coreSwitch, aggrSwitch2 )
    net.addLink( aggrSwitch2, edgeSwitch2 )
    net.addLink( edgeSwitch2, host2 )


    info( '*** Starting network\n')
    net.start()

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    createTreeTopo()
