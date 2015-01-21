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

def createTopo(  ):
    "Simple topology example."


    net = Mininet( controller=RemoteController)

    info( '*** Adding controller\n' )
    net.addController( 'c0', controller=RemoteController,ip="127.0.0.1",port=6633 )

    # Add hosts and switches
    leftHost = net.addHost( 'h1' )
    rightHost = net.addHost( 'h2' )
    leftSwitch = net.addSwitch( 's3' )
    rightSwitch = net.addSwitch( 's4' )
    centerSwitchl = net.addSwitch( 's5' )
    centerSwitchr = net.addSwitch( 's6' )

    # Add links
    net.addLink( leftHost, leftSwitch )
    net.addLink( leftSwitch, centerSwitchl )
    net.addLink( centerSwitchl, centerSwitchr )
    net.addLink( centerSwitchr, rightSwitch)

    linkOpts = {'bw':10};
    net.addLink( rightSwitch, rightHost, cls=TCLink, **linkOpts)


    info( '*** Starting network\n')
    net.start()

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    createTopo()


