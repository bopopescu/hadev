import os
import sys

from optparse import OptionParser


parser = OptionParser();

parser.add_option("-o", "--queueName", dest="queueName",
        help="qos name to be used", default="NoQueueName");

(options, args) = parser.parse_args();



if options.queueName != "NoQueueName":

    command = 'sudo ovs-vsctl -- destroy queue %s' % (options.queueName);

    result = os.popen(command);

    qIds=result.readlines();
    for qId in qIds:
        print qId;

