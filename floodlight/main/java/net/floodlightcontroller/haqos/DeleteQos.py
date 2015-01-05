import os
import sys

from optparse import OptionParser


parser = OptionParser();

parser.add_option("-o", "--qosName", dest="qosName",
        help="qos name to be used", default="NoQosName");

parser.add_option("-o", "--portName", dest="portName",
        help="qos name to be used", default="NoPortName");
(options, args) = parser.parse_args();



if options.qosName != "NoQosName" or options.portName != "NoPortName":

    command = 'sudo ovs-vsctl -- clear port %s qos' % (options.portName);

    result = os.popen(command);

    qIds=result.readlines();
    for qId in qIds:
        print qId;

    command = 'sudo ovs-vsctl -- destroy qos %s' % (options.qosName);

    result = os.popen(command);

    qIds=result.readlines();
    for qId in qIds:
        print qId;
