/**
 *    Copyright 2013, Big Switch Networks, Inc.
 *
 *    Licensed under the Apache License, Version 2.0 (the "License"); you may
 *    not use this file except in compliance with the License. You may obtain
 *    a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 *    Unless required by applicable law or agreed to in writing, software
 *    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 *    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 *    License for the specific language governing permissions and limitations
 *    under the License.
 **/

package net.floodlightcontroller.haqos.web;

import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import net.floodlightcontroller.packet.IPv4;

import net.floodlightcontroller.core.IFloodlightProviderService;
import net.floodlightcontroller.core.IOFSwitch;
import net.floodlightcontroller.core.annotations.LogMessageDoc;
import net.floodlightcontroller.haqos.IHaqosService;

import org.openflow.protocol.OFMatch;
import org.openflow.protocol.OFPort;
import org.openflow.protocol.OFQueueGetConfigRequest;
import org.openflow.protocol.OFQueueGetConfigReply;
import org.openflow.protocol.OFPacketQueue;


import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.databind.MappingJsonFactory;
import org.restlet.data.Status;
import org.restlet.resource.Delete;
import org.restlet.resource.Get;
import org.restlet.resource.Post;
import org.restlet.resource.Put;
import org.restlet.resource.ServerResource;
import org.openflow.util.HexString;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HaqosResourceBase extends ServerResource {
    protected static Logger log = LoggerFactory.getLogger(HaqosResource.class);
    
    
    public List <OFPacketQueue> getQueuesOnSwitch(long switchId) {
        
        IFloodlightProviderService floodlightProvider =
                (IFloodlightProviderService)getContext().getAttributes().
                    get(IFloodlightProviderService.class.getCanonicalName());

        IOFSwitch sw = floodlightProvider.getSwitch(switchId);
        Future<List<OFPacketQueue>> future;
        List<OFPacketQueue> values = null;
        if (sw != null) {
            OFQueueGetConfigRequest req =
                new OFQueueGetConfigRequest(OFPort.OFPP_NONE.getValue());
            //int requestLength = req.getLengthU();
            //req.setLengthU(requestLength);
            try {
                future = sw.queueGetConfig(req);
                values = future.get(10, TimeUnit.SECONDS);
            } catch (Exception e) {
                log.error("Failure retrieving queues from switch " + sw, e);
            }
        }
        return values;
    }

    public List <OFPacketQueue> getQueuesOnSwitch(String switchId) {
        return getQueuesOnSwitch(HexString.toLong(switchId));
    }


    public boolean createQueuesOnPath(
        long srcId,
        String srcPort,
        long dstId,
        String dstPort,
        long bandwidth) {

        IHaqosService haqos =
                (IHaqosService)getContext().getAttributes().
                    get(IHaqosService.class.getCanonicalName());

        haqos.createQueuesOnPath(srcId,
                                srcPort,
                                dstId,
                                dstPort,
                                bandwidth);
        return true;
    }

}
