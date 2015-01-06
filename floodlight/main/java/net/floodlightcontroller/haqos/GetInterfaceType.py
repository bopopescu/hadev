import os
import sys

from optparse import OptionParser


parser = OptionParser();

parser.add_option("-o", "--intName", dest="interface",
        help="interface name to be used", default="NoInterface");

(options, args) = parser.parse_args();



if options.interface != "NoInterface":

    command = 'sudo ovs-vsctl list Interface %s | grep type' % (options.interface);

    result = os.popen(command);

    intType=result.readlines();
    for line in intType:
        (typeK,sep, typeV) = line.partition(':');
        typeV = typeV.strip();
        if typeV == 'gre' or typeV == 'vxlan':
            print 1;
        else:
            print 0;

