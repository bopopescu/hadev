
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

package net.floodlightcontroller.haqos;

import java.io.*;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.lang.Process;
import java.lang.ProcessBuilder;
import java.util.List;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import net.floodlightcontroller.core.FloodlightContext;
import net.floodlightcontroller.core.HAListenerTypeMarker;
import net.floodlightcontroller.core.IFloodlightProviderService;
import net.floodlightcontroller.core.IHAListener;
import net.floodlightcontroller.core.IOFMessageListener;
import net.floodlightcontroller.core.IOFSwitch;
import net.floodlightcontroller.core.IOFSwitchListener;
import net.floodlightcontroller.core.ImmutablePort;
import net.floodlightcontroller.core.annotations.LogMessageCategory;
import net.floodlightcontroller.core.annotations.LogMessageDoc;
import net.floodlightcontroller.core.module.FloodlightModuleContext;
import net.floodlightcontroller.core.module.FloodlightModuleException;
import net.floodlightcontroller.core.module.IFloodlightModule;
import net.floodlightcontroller.core.module.IFloodlightService;
import net.floodlightcontroller.core.util.AppCookie;
import net.floodlightcontroller.restserver.IRestApiService;
import net.floodlightcontroller.staticflowentry.web.StaticFlowEntryWebRoutable;
import net.floodlightcontroller.storage.IResultSet;
import net.floodlightcontroller.storage.IStorageSourceListener;
import net.floodlightcontroller.storage.IStorageSourceService;
import net.floodlightcontroller.storage.StorageException;
import net.floodlightcontroller.linkdiscovery.ILinkDiscoveryListener;
import net.floodlightcontroller.linkdiscovery.ILinkDiscoveryService;
import net.floodlightcontroller.haqos.web.HaqosWebRoutable;
import net.floodlightcontroller.restserver.IRestApiService;
import net.floodlightcontroller.routing.IRoutingService;
import net.floodlightcontroller.routing.Route;
import net.floodlightcontroller.routing.RouteId;
import net.floodlightcontroller.topology.ITopologyService;
import net.floodlightcontroller.topology.ITopologyListener;
import net.floodlightcontroller.topology.NodePortTuple;
import net.floodlightcontroller.threadpool.IThreadPoolService;
import net.floodlightcontroller.linkdiscovery.ILinkDiscovery.LDUpdate;
import net.floodlightcontroller.linkdiscovery.ILinkDiscoveryService;

import org.openflow.protocol.OFFlowMod;
import org.openflow.protocol.OFFlowRemoved;
import org.openflow.protocol.OFMatch;
import org.openflow.protocol.OFMessage;
import org.openflow.protocol.OFType;
import org.openflow.protocol.OFMatch;
import org.openflow.protocol.OFPort;
import org.openflow.protocol.statistics.OFStatistics;
import org.openflow.protocol.statistics.OFStatisticsType;
import org.openflow.protocol.OFStatisticsRequest;
import org.openflow.protocol.statistics.OFQueueStatisticsRequest;
import org.openflow.util.HexString;
import org.openflow.util.U16;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@LogMessageCategory("HA QoS")
/**
 * This module is responsible for QoS and HA for cloud apps using OVS
 * switches. This is just a big 'ol dumb list of flows and something external
 * is responsible for ensuring they make sense for the network.
 */


public class Haqos
    implements IFloodlightModule, IHaqosService,
               IOFMessageListener, ITopologyListener {
    protected static Logger log = LoggerFactory.getLogger(Haqos.class);


    public static final String MODULE_NAME = "haqos";

    //protected ILinkDiscoveryService linkDiscovery;
    //protected IThreadPoolService threadPool;
    protected IFloodlightProviderService floodlightProvider;
    protected ITopologyService topology;
    protected IRoutingService routingEngine;
    protected IRestApiService restApi;

    protected HashMap<String /*Switch DPID*/, String /*qosId*/ > qosMap;

    protected HashMap<String /*Switch DPID*/, List<String> /*List of queueId*/ > queueMap;

    protected HashMap<RouteId, Route> routeMap;
    protected HashMap<RouteId, Short> sourcePortMap;
    protected HashMap<RouteId, Short> destPortMap;

    protected HashMap<RouteId, Long> bandwidthMap;

    protected HashMap<Short /*Port number*/, List<RouteId> /*List of routes associated*/ > portRouteMap;

    @Override
    public void printTest() {
    }


    @Override
    public void topologyChanged(List<LDUpdate> appliedUpdates) {
        for (RouteId routeId : routeMap.keySet()) {
          Route route = routeMap.get(routeId);
          short srcPort = sourcePortMap.get(routeId).shortValue();
          short dstPort = destPortMap.get(routeId).shortValue();
          Route newRoute = routingEngine.getRoute(routeId.getSrc(), srcPort,
                                    routeId.getDst(), dstPort, 0);
          if (newRoute != route) {
              /*Need to update the queues*/
          }
        }
    }


    @Override
    public List <OFStatistics> getQueuesOnSwitch(long switchId) {
        
        IOFSwitch sw = floodlightProvider.getSwitch(switchId);
        Future<List<OFStatistics>> future;
        List<OFStatistics> values = null;
        if (sw != null) {
            OFStatisticsRequest req = new OFStatisticsRequest();
            req.setStatisticType(OFStatisticsType.QUEUE);
            int reqLength = req.getLengthU();
            OFQueueStatisticsRequest specReq = new OFQueueStatisticsRequest();
            specReq.setPortNumber(OFPort.OFPP_ALL.getValue());
            specReq.setQueueId(0xffffffff);
            req.setStatistics(Collections.singletonList((OFStatistics)specReq));
            reqLength += specReq.getLength();
            req.setLengthU(reqLength);
            try {
                future = sw.queryStatistics(req);
                values = future.get(10, TimeUnit.SECONDS);
                log.info("after getting values");
            } catch (Exception e) {
                log.error("Failure retrieving queues from switch " + sw, e);
            }
        }
        return values;
    }



    private void callOvsUsingProcess(String[] command, String srcPort) {

        try {
            log.info(" before start ");
            Process cmdProcess = new ProcessBuilder(command).start();
            log.info(" after start ");
            InputStream inputStream = cmdProcess.getInputStream();
            InputStreamReader inputReader = new InputStreamReader(inputStream);
            BufferedReader bufReader = new BufferedReader(inputReader);
            String line;
            int i = 0;
            List<String> qidList = new ArrayList<String> ();
            while ((line = bufReader.readLine()) != null) {
                if (line == "") {
                    continue;
                }
                if (i == 0) {
                    qosMap.put(srcPort, line);
                } else {
                    qidList.add(line);
                }
                i += 1;
                log.info(line);
            }
            queueMap.put(srcPort, qidList);
        } catch (IOException e) {
            log.info("io exception ");
        }
    }

    private long getUpdatedBandwidth(short portId, RouteId addRoute, long bandwidth)
    {
        List<RouteId> routesOnPort = portRouteMap.get(portId);
        ListIterator<RouteId> iter = routesOnPort.listIterator();
        long updatedBandwidth = bandwidth;
        boolean alreadyAdded = false;
        while (iter.hasNext()) {
            RouteId routeId = iter.next();
            if (routeId == addRoute) {
                alreadyAdded = true;
                continue;
            }
            updatedBandwidth += bandwidthMap.get(routeId).longValue();
        }
        if (alreadyAdded == false) {
            routesOnPort.add(addRoute);
            portRouteMap.put(portId, routesOnPort);
        }
        return updatedBandwidth;
    }

    @Override
    public void createQueuesOnPath(long srcId,
        String srcPort, long dstId, String dstPort, long bandwidth) {
        /* 
         * Create egress queue based on srcPort if srcId = dstId
         */
        IOFSwitch sw = floodlightProvider.getSwitch(srcId);
        ImmutablePort port = sw.getPort(srcPort);
        short portNum = port.getPortNumber();

        ImmutablePort dstImmPort = sw.getPort(dstPort);
        short dstPortNum = dstImmPort.getPortNumber();

        if (srcId == dstId) {
            String qosName = "qos" + portNum;
            String queueName = "qu" + portNum;
            String[] command = {"python",
                "/home/snathan/floodlight-master/src/main/java/net/floodlightcontroller/haqos/CreateQueues.py",
                "--qName=" + queueName, "--srcPort=" + srcPort, "--qosName=" + qosName, "--qNum=" + portNum,
                "--bandwidth=" + bandwidth};

            callOvsUsingProcess(command, srcPort);
        } else {
            Route route =
                routingEngine.getRoute(srcId, portNum, dstId, dstPortNum, 0);
            List<NodePortTuple> switches = route.getPath();
            ListIterator<NodePortTuple> iter = switches.listIterator();
            int i = 0;
            if (switches != null && switches.isEmpty() == false) {
                routeMap.put(route.getId(), route);
                sourcePortMap.put(route.getId(), new Short(portNum));
                destPortMap.put(route.getId(), new Short(dstPortNum));
                bandwidthMap.put(route.getId(), new Long(bandwidth));
            }
            while(iter.hasNext()) {
                NodePortTuple tuple = iter.next();
                long switchId = tuple.getNodeId();
                long useBandwidth = bandwidth;
                i += 1;
                if (switchId == srcId || switchId == dstId) {
                    continue;
                }
                if ((i % 2) == 0) {
                    continue;
                }
                short portId = tuple.getPortId();
                if (portRouteMap.containsKey(portId)) {
                     useBandwidth = getUpdatedBandwidth(portId, route.getId(), bandwidth);
                } else {
                    List<RouteId> routes = new ArrayList<RouteId>();
                    routes.add(route.getId());
                    portRouteMap.put(portId, routes);
                }
                sw = floodlightProvider.getSwitch(switchId);
                port = sw.getPort(portId);
                String portName = port.getName();
                String qosName = "qos" + portId;
                String queueName = "qu" + portId;
                String[] command = {"python",
                  "/home/snathan/floodlight-master/src/main/java/net/floodlightcontroller/haqos/CreateQueues.py",
                  "--qName=" + queueName, "--srcPort=" + portName, "--qosName=" + qosName, "--qNum=" + portId,
                  "--bandwidth=" + useBandwidth};
                callOvsUsingProcess(command, portName);
            }

        }
    }

    @Override
    public Collection<Class<? extends IFloodlightService>> getModuleServices() {
        Collection<Class<? extends IFloodlightService>> l =
                new ArrayList<Class<? extends IFloodlightService>>();
        l.add(IHaqosService.class);
        return l;
    }


    @Override
    public Map<Class<? extends IFloodlightService>, IFloodlightService>
            getServiceImpls() {
        Map<Class<? extends IFloodlightService>,
        IFloodlightService> m =
            new HashMap<Class<? extends IFloodlightService>,
                IFloodlightService>();
        // We are the class that implements the service
        m.put(IHaqosService.class, this);
        return m;
    }


    @Override
    public Collection<Class<? extends IFloodlightService>>
            getModuleDependencies() {
        Collection<Class<? extends IFloodlightService>> l =
                new ArrayList<Class<? extends IFloodlightService>>();
        //l.add(ILinkDiscoveryService.class);
        //l.add(IThreadPoolService.class);
        l.add(IFloodlightProviderService.class);
        l.add(ITopologyService.class);
        l.add(IRoutingService.class);
        l.add(IRestApiService.class);
        return l;
    }


    @Override
    public void init(FloodlightModuleContext context)
            throws FloodlightModuleException {
        //linkDiscovery = context.getServiceImpl(ILinkDiscoveryService.class);
        //threadPool = context.getServiceImpl(IThreadPoolService.class);
        floodlightProvider =
                context.getServiceImpl(IFloodlightProviderService.class);
        topology = context.getServiceImpl(ITopologyService.class);
        routingEngine = context.getServiceImpl(IRoutingService.class);
        restApi = context.getServiceImpl(IRestApiService.class);

        qosMap = new HashMap<String, String> ();
        queueMap = new HashMap<String, List<String>> ();
        routeMap = new HashMap<RouteId, Route> ();
        sourcePortMap = new HashMap<RouteId, Short> ();
        destPortMap = new HashMap<RouteId, Short> ();
        bandwidthMap = new HashMap<RouteId, Long> ();
        portRouteMap = new HashMap<Short, List<RouteId>> ();
        log.info("at init of Haqos");

    }


    @Override
    public void startUp(FloodlightModuleContext context) {
        floodlightProvider.addOFMessageListener(OFType.PACKET_IN, this);
        restApi.addRestletRoutable(new HaqosWebRoutable());
        topology.addListener(this);
        log.info("at startUp of Haqos");
    }


    @Override
    public String getName() {
        return MODULE_NAME;
    }

    @Override
    public boolean isCallbackOrderingPrereq(OFType type, String name) {
        return "linkdiscovery".equals(name);
    }

    @Override
    public boolean isCallbackOrderingPostreq(OFType type, String name) {
        return false;
    }

    @Override
    public Command receive(IOFSwitch sw, OFMessage msg,
                           FloodlightContext cntx) {

        return Command.CONTINUE;
    }

}
