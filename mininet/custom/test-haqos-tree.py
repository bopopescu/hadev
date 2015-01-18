"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.net import Mininet



class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."
        Topo.__init__(self);
        # Add hosts and switches
        host1 = self.addHost( 'h1' )
        host2 = self.addHost( 'h2' )
        #host3 = self.addHost( 'h3' )
        #host4 = self.addHost( 'h4' )
        edgeSwitch1 = self.addSwitch( 's3' )
        edgeSwitch2 = self.addSwitch( 's4' )
        #edgeSwitch3 = self.addSwitch( 'e3' )
        #edgeSwitch4 = self.addSwitch( 'e4' )
        aggrSwitch1 = self.addSwitch( 's5' )
        aggrSwitch2 = self.addSwitch( 's6' )
        coreSwitch = self.addSwitch( 's7' )

        # Add links
        self.addLink( host1, edgeSwitch1 )
        self.addLink( edgeSwitch1, aggrSwitch1 )
        self.addLink( aggrSwitch1, coreSwitch )
        self.addLink( coreSwitch, aggrSwitch2 )
        self.addLink( aggrSwitch2, edgeSwitch2 )
        self.addLink( edgeSwitch2, host2 )
        #self.addLink( host3, edgeSwitch3 )
        #self.addLink( edgeSwitch3, aggrSwitch1 )


topos = { 'mytopo': ( lambda: MyTopo() ) }
