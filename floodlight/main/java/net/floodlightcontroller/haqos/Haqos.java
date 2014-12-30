
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

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

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
import net.floodlightcontroller.topology.ITopologyService;
import net.floodlightcontroller.threadpool.IThreadPoolService;

import org.openflow.protocol.OFFlowMod;
import org.openflow.protocol.OFFlowRemoved;
import org.openflow.protocol.OFMatch;
import org.openflow.protocol.OFMessage;
import org.openflow.protocol.OFType;
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
    implements IFloodlightModule, IHaqosService,IOFMessageListener {
    protected static Logger log = LoggerFactory.getLogger(Haqos.class);


    public static final String MODULE_NAME = "haqos";

    //protected ILinkDiscoveryService linkDiscovery;
    //protected IThreadPoolService threadPool;
    protected IFloodlightProviderService floodlightProvider;
    //protected ITopologyService topology;
    //protected IRoutingService routing;
    protected IRestApiService restApi;


    @Override
    public void printTest() {
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
        //l.add(ITopologyService.class);
        //l.add(IRoutingService.class);
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
        //topology = context.getServiceImpl(ITopologyService.class);
        //routing = context.getServiceImpl(IRoutingService.class);
        restApi = context.getServiceImpl(IRestApiService.class);
        log.info("at init of Haqos");

    }


    @Override
    public void startUp(FloodlightModuleContext context) {
        floodlightProvider.addOFMessageListener(OFType.PACKET_IN, this);
        restApi.addRestletRoutable(new HaqosWebRoutable());
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
