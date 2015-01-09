import os
import sys

from optparse import OptionParser


parser = OptionParser();

parser.add_option("-t", "--tunId", dest="tunnelId",
        help="Tunnel Id to be used", default="NoTunnel");

parser.add_option("-i", "--inPort", dest="inputPort",
        help="input Port to be used", default="NoInputPort");

parser.add_option("-p", "--tcpPort", dest="tcpPort",
        help="TCP port to be used", default="NoTcpPort");

parser.add_option("-o", "--outPort", dest="outPort",
        help="out port to be used", default="NoOutPort");

parser.add_option("-d", "--dscpVal", dest="DscpVal",
        help="DSCP val to be used in TOS", default="NoDscp");

parser.add_option("-b", "--brName", dest="brName",
        help="Name of the bridge", default="NoBridge");


(options, args) = parser.parse_args();



if options.tunnelId != "NoTunnel":

    command = 'sudo ovs-ofctl add-flow %s dl_type=0x0800,nw_proto=6,in_port=%s,tp_src=%s,actions=set_tunnel:%s,mod_nw_tos:%s,enqueue:%s:%s' % (options.brName, options.inputPort, options.tcpPort, options.tunnelId, options.DscpVal, options.outPort, options.outPort);

    result = os.popen(command);

    output=result.readlines();
    for line in output:
        print line;
