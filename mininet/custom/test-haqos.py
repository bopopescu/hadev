"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )


        # Build 16 hosts 
        hosts = [];
        i = 0;
        while (i < 16):
            hosts.append(self.addHost('h%s' % (i+1)));
            i += 1;

        # Build 2 Core switches
        core = [];
        j = 0;
        while (j < 2):
            core.append(self.addSwitch('s%s' % (i+1)));
            i += 1;
            j += 1;

        # Build 4 Aggr switches
        aggr = [];
        j = 0;
        while (j < 4):
            aggr.append(self.addSwitch('s%s' % (i+1)));
            i += 1;
            j += 1;

        # Build 8 Edge switches
        edge = [];
        j = 0;
        while (j < 8):
            edge.append(self.addSwitch('s%s' % (i+1)));
            i += 1;
            j += 1;


        # Link aggr with core 
        i = 0;
        while (i < 4):
            j = 0;
            while j < 2:
                self.addLink (aggr[i], core[j]);
                j += 1;
            i += 1;

        # Link edge with aggr
        i = 0;
        while (i < 8):
            j = i / 2;
            self.addLink (edge[i], aggr[j]);
            i += 1;

        # Link host with edge
        i = 0;
        while (i < 16):
            j = i / 2;
            self.addLink (hosts[i], edge[j]);
            i += 1;


topos = { 'mytopo': ( lambda: MyTopo() ) }
