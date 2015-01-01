import os
import sys

from optparse import OptionParser


parser = OptionParser();

parser.add_option("-q", "--qName", dest="queueName",
        help="queue Name to be used", default="NoName");


parser.add_option("-n", "--qNum", dest="queueNum",
        help="queue Num to be used", default=0);

parser.add_option("-p", "--srcPort", dest="srcPort",
        help="source Port", default=0);


parser.add_option("-b", "--bandwidth", dest="bandwidth",
        help="bandwidth", default=20);

parser.add_option("-o", "--qosName", dest="qosName",
        help="qos name to be used", default="NoQosName");

(options, args) = parser.parse_args();



if options.queueName != "NoName" or options.qosName != "NoQosName":

    command = 'sudo ovs-vsctl -- set port %s qos=@%s -- --id=@%s create qos type=linux-htb other-config:min-rate=%s queues:%s=@%s -- --id=@%s create Queue other-config:min-rate=%s' % (options.srcPort, options.qosName, options.qosName, options.bandwidth, options.queueNum, options.queueName, options.queueName, options.bandwidth);

    result = os.popen(command);

    qIds=result.readlines();
    for qId in qIds:
        print qId;
