#!/usr/bin/python
import sys
sys.path.append("..")
import socket
from SFlow import sflow
import numpy as np
from config.read import read_topo 
def form(file = "config/topo.json"):
    raw = read_topo(file)
    hosts = []
    racks = []
    for rack in raw[1:]:
        racks.append(rack['ip'][0])
        hosts += rack['host'].keys()
    # print(hosts)
    # print(racks)
    return hosts,racks
    
def sampling(UDP_IP, UDP_PORT, SlotLen, hosts, racks):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    slotcnt = 0
    host_num = len(hosts)
    rack_num = len(racks)
    tf_hosts = np.zeros(shape=(host_num,host_num))
    # tf_racks = np.zeros(shape=(rack_num,rack_num))
    while True:
        data, addr = sock.recvfrom(3000) # 1386 bytes is the largest possible sFlow packet, by spec 3000 seems to be the number by practice
        sFlowData = sflow.sFlow(data)
        # Below this point is test code.
        # print("Source:", addr[0])
        # print("length:", sFlowData.len)
        # print("DG Version:", sFlowData.dgVersion)
        # print("Address Type:", sFlowData.addressType)
        # print("Agent Address:", sFlowData.agentAddress)
        # print("Sub Agent:", sFlowData.subAgent)
        # print("Sequence Number:", sFlowData.sequenceNumber)
        # print("System UpTime:", sFlowData.sysUpTime)
        if slotcnt == 0: 
            slotcnt = sFlowData.sysUpTime // SlotLen
        if sFlowData.sysUpTime > (slotcnt + 1) * SlotLen:
            slotcnt += 1
            print(tf_hosts, sFlowData.sysUpTime)
            tf_hosts = np.zeros(shape=(host_num,host_num))
        # print("Number of Samples:", sFlowData.NumberSample)
        for i in range(sFlowData.NumberSample):
            #print "Sample Number:", i + 1
            #print("Sample Sequence:", sFlowData.samples[i].sequence)
            #print("Sample Enterprise:", sFlowData.samples[i].enterprise)
            #print("Sample Type:", sFlowData.samples[i].sampleType)
            # print("Sample Length:", sFlowData.samples[i].len)
            #print("Sample Source Type:", sFlowData.samples[i].sourceType)
            #print("Sample Source Index:", sFlowData.samples[i].sourceIndex)
            #print("Sample Rate:", sFlowData.samples[i].sampleRate)
            #print("Sample Pool:", sFlowData.samples[i].samplePool)
            #print("Sample Dropped Packets:", sFlowData.samples[i].droppedPackets)
            #print("Sample Input Interface:", sFlowData.samples[i].inputInterface)
            #print("Sample Output Interface:", sFlowData.samples[i].outputInterface)
            #print "Sample Record Count:", sFlowData.samples[i].recordCount
            #print()
            for j in range(sFlowData.samples[i].recordCount):
                # print "Record Header:", sFlowData.samples[i].records[j].header
                # print("Record Enterprise:", sFlowData.samples[i].records[j].enterprise)
                # print("Record Sample Type:", sFlowData.samples[i].records[j].sampleType)
                # print("Record Format:", sFlowData.samples[i].records[j].format)
                # print("Record Length:", sFlowData.samples[i].records[j].len)
                if sFlowData.samples[i].records[j].sampleType == 1:
                    if sFlowData.samples[i].records[j].format == 1 and sFlowData.samples[i].records[j].enterprise == 0:
                        record = sflow.sFlowRawPacketHeader(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        # print ("srcIp:",record.srcIp)
                        # print ("dstIp:",record.dstIp)
                        src, dst = record.srcIp, record.dstIp
                        if src in hosts and dst in hosts:
                            tf_hosts[hosts.index(src)][hosts.index(dst)] += record.frameLength   
                        
                        # print ("srcPort:",record.srcPort)
                        # print ("dstPort:",record.dstPort)
                        # print("Raw Packet Header Protocol:", record.headerProtocol)
                        # print("Frame Length:", record.frameLength)
                        # print("Payload Removed:", record.payloadRemoved)
                        # print("Header Size:", record.headerSize)
                        # print("Flow 1")                
                    elif sFlowData.samples[i].records[j].format == 2 and sFlowData.samples[i].records[j].enterprise == 0:
                        record = sflow.sFlowEthernetFrame(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print "Ethernet Frame Length:", record.frameLength
                        #print "Ethernet Frame src MAC:", record.srcMAC
                        #print "Ethernet Frame dst MAC:", record.dstMAC
                        #print "Ethernet Frame Record Type:", record.type
                        # print("Flow 2")
                    elif sFlowData.samples[i].records[j].format == 1001:
                        record = sflow.sFlowExtendedSwitch(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        # print("srcVLAN:", record.srcVLAN)
                        # print("srcPriority:", record.srcPriority)
                        # print("dstVLAN:", record.dstVLAN)
                        # print("dstPriority:", record.dstPriority)
                        # print("Flow 1001")
                    elif sFlowData.samples[i].records[j].enterprise == 8800:
                        # Obsolete Enterprise - https://github.com/pmacct/pmacct/issues/71
                        #print("Flow Record Enterprise 8800 - Obsolete")
                        #print("Flow Record Type:", sFlowData.samples[i].records[j].format)
                        pass
                    else:
                        pass
                        # print("Flow Record Enterprise:", sFlowData.samples[i].records[j].enterprise)
                        # print("Flow Record Type:", sFlowData.samples[i].records[j].format)
                elif sFlowData.samples[i].records[j].sampleType == 2:
                    if sFlowData.samples[i].records[j].format == 1:
                        record = sflow.sFlowIfCounters(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        # print ("If Counter Index:", record.index)
                        # print ("If Counter Type:", record.type)
                        # print ("If Counter Speed:", record.speed)
                        # print ("If Counter Direction:", record.direction)
                        # print ("If Counter Status:", record.status)
                        # print ("If Counter I Octets:", record.inputOctets)
                        # print ("If Counter I Packets:", record.inputPackets)
                        # print ("If Counter I Multicast:", record.inputMulticast)
                        # print ("If Counter I Broadcast:", record.inputBroadcast)
                        # print ("If Counter I Discards:", record.inputDiscarded)
                        # print ("If Counter I Errors:", record.inputErrors)
                        # print ("If Counter I Unknown:", record.inputUnknown) 
                        # print ("If Counter O Octets:", record.outputOctets)
                        # print ("If Counter O Packets:", record.outputPackets)
                        # print ("If Counter O Multicast:", record.outputMulticast)
                        # print ("If Counter O Broadcast:", record.outputBroadcast)
                        # print ("If Counter O Discard:", record.outputDiscarded)
                        # print ("If Counter O Errors:", record.outputErrors)
                        # print ("If Counter Promiscuous:", record.promiscuous)
                        # print("Counter 1")
                    elif sFlowData.samples[i].records[j].format == 2:
                        record = sflow.sFlowEthernetInterface(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print "Ethernet Alignmet Error:", record.alignmentError
                        #print "Ethernet FCS Error:", record.fcsError
                        #print "Ethernet Single Collision Frames:", record.singleCollision
                        #print "Ethernet Multiple Collision Frames:", record.multipleCollision
                        #print "Ethernet SQE Test Error:", record.sqeTest
                        #print "Ethernet Deferred Transmissions:", record.deferred
                        #print "Ethernet Late Collisions:", record.lateCollision
                        #print "Ethernet Excessiove Collisions:", record.excessiveCollision
                        #print "Ethernet Internal Transmit Error:", record.internalTransmitError
                        #print "Ethernet Carrier Sense Error:", record.carrierSenseError
                        #print "Ethernet Frame Too Long:", record.frameTooLong
                        #print "Ethernet Internal Receive Error:", record.internalReceiveError
                        #print "Ethernet Symbol Error:", record.symbolError
                        # print("Counter 2")
                    elif sFlowData.samples[i].records[j].format == 5:
                        record = sflow.sFlowVLAN(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        # print "VLAN :", record.vlanID
                        # print "VLAN :", record.octets
                        # print "VLAN :", record.unicast
                        # print "VLAN :", record.multicast
                        # print "VLAN :", record.broadcast
                        # print "VLAN :", record.discard
                        # print("Counter 5")
                    elif sFlowData.samples[i].records[j].format == 1001:
                        record = sflow.sFlowProcessor(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        # print "Processor :", record.cpu5s 
                        # print "Processor :", record.cpu1m  
                        # print "Processor :", record.cpu5m
                        # print("Processor :", record.totalMemory) 
                        # print("Processor :", record.freeMemory)
                        # print("Counter 1001")
                    elif sFlowData.samples[i].records[j].format == 1004:
                        record = sflow.sFlowOfPort(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        # print("datapathId:", record.datapathId)
                        # print("port No.:", record.portNo)
                        # print("Counter 1004")
                    elif sFlowData.samples[i].records[j].format == 1005:
                        record = sflow.sFlowPortName(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        # print("Port Name", record.PortName)
                        # print("Counter 1005")
                    """elif sFlowData.samples[i].records[j].format == 2000:
                        record = sflow.sFlowHostDescr(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print("Counter 2000")
                    elif sFlowData.samples[i].records[j].format == 2001:
                        record = sflow.sFlowHostAdapters(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print "Host Adpaters:", record.adapaters
                        #print("Counter 2001")
                    elif sFlowData.samples[i].records[j].format == 2002:
                        record = sflow.sFlowHostParent(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print "Host Parent Container Type:", record.containerType
                        #print "Host Parent Container Index:", record.containerIndex
                        #print("Counter 2002")
                    elif sFlowData.samples[i].records[j].format == 2003:
                        record = sflow.sFlowHostCPU(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print("Counter 2003")
                    elif sFlowData.samples[i].records[j].format == 2004:
                        record = sflow.sFlowHostMemory(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print "Host Memory Total:", record.memTotal
                        #print "Host Memory Free:", record.memFree
                        #print "Host Memory Shared:", record.memShared
                        #print "Host Memory Buffers:", record.memBuffers
                        #print "Host Memory Cache:", record.memCache
                        #print "Host Swap Memory Total:", record.swapTotal
                        #print "Host Swap Memory Free:", record.swapFree
                        #print "Host Page In:", record.pageIn
                        #print "Host Page Out:", record.pageOut
                        #print "Host Swap Page In:", record.swapIn
                        #print "Host Swap Page Out:", record.swapOut
                        #print("Counter 2004")
                    elif sFlowData.samples[i].records[j].format == 2005:
                        record = sflow.sFlowHostDiskIO(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print "Host disk:", record.diskTotal
                        #print "Host disk:", record.diskFree
                        #print "Host disk:", record.partMaxused
                        #print "Host disk:", record.read
                        #print "Host disk:", record.readByte
                        #print "Host disk:", record.readTime
                        #print "Host disk:", record.write
                        #print "Host disk:", record.writeByte
                        #print "Host disk:", record.writeTime
                        #print("Counter 2005")
                    elif sFlowData.samples[i].records[j].format == 2006:
                        record = sflow.sFlowHostNetIO(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print("Counter 2006")
                    elif sFlowData.samples[i].records[j].format == 2007:
                        record = sflow.sFlowMib2IP(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print("Counter 2007")
                    elif sFlowData.samples[i].records[j].format == 2008:
                        record = sflow.sFlowMib2ICMP(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print("Counter 2008")
                    elif sFlowData.samples[i].records[j].format == 2009:
                        record = sflow.sFlowMib2TCP(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print "TCP Algorithm:", record.algorithm
                        #print "TCP RTO Min:", record.rtoMin
                        #print "TCP RTO Max:", record.rtoMax
                        #print "TCP Max Connections:", record.maxConnection
                        #print "TCP Active Open:", record.activeOpen
                        #print "TCP Passive Open:", record.passiveOpen
                        #print "TCP Attempt Fail:", record.attemptFail
                        #print "TCP Established Reset:", record.establishedReset
                        #print "TCP Current Established:", record.currentEstablished
                        #print "TCP In Segments:", record.inSegment
                        #print "TCP Out Segments:", record.outSegment
                        #print "TCP Retransmit Segemnt:", record.retransmitSegment
                        #print "TCP In Error:", record.inError
                        #print "TCP Out Reset:", record.outReset
                        #print "TCP In C sum Error:", record.inCsumError
                        #print("Counter 2009")
                    elif sFlowData.samples[i].records[j].format == 2010:
                        record = sflow.sFlowMib2UDP(sFlowData.samples[i].records[j].len, sFlowData.samples[i].records[j].data)
                        #print "Counter 2010"
                        #print "UDP In Datagrams:", record.inDatagrams
                        #print "UDP No Ports:", record.noPorts
                        #print "UDP In Errors:", record.inErrors
                        #print "UDP Out Datagrams:", record.outDatagrams
                        #print "UDP Receive Buffer Error:", record.receiveBufferError
                        #print "UDP Send Buffer Error:", record.sendBufferError 
                        #print "UDP In Check Sum Error:", record.inCheckSumError
                        #print("Counter 2010") 
                    else:
                        print("Counter Record Enterprise:", sFlowData.samples[i].records[j].enterprise)
                        print("Counter Record Type:", sFlowData.samples[i].records[j].format)"""
                else:
                    pass
                    # print("Sample Type", sFlowData.samples[i].records[j].sampleType)
                    # print("Sample Record Enterprise:", sFlowData.samples[i].records[j].enterprise)
                    # print("Sample Record Type:", sFlowData.samples[i].records[j].format)

hosts, racks = form("config/topo.json")
UDP_IP = "127.0.0.1"
UDP_PORT = 6343
SlotLen = 5000
sampling(UDP_IP, UDP_PORT, SlotLen, hosts, racks)    
