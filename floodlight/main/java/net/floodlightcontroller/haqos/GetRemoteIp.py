import os
import sys

from optparse import OptionParser


parser = OptionParser();

parser.add_option("-o", "--intName", dest="interface",
        help="interface name to be used", default="NoInterface");

(options, args) = parser.parse_args();



if options.interface != "NoInterface":

    command = 'sudo ovs-vsctl list Interface %s | grep remote_ip' % (options.interface);

    result = os.popen(command);

    intType=result.readlines();
    for line in intType:
        index = line.find('"');
        newStr = line[index+1:]
        index = newStr.find('"');
        newStr = newStr[:index]
        print newStr;

