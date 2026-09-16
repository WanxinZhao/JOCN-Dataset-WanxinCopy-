#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/wifi-module.h"
#include "ns3/lte-module.h"
#include "ns3/csma-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include <fstream>
#include <map>
#include <string>

using namespace ns3;

int main(int argc, char *argv[])
{
    double simTime = 10.0;
    int seed = 1;
    std::string outputDir = ".";
    double offeredLoadMbps = 10.0;
    uint32_t packetSize = 1024;
    double mobilitySpeed = 1.5;
    double lifiRateMbps = 100.0;

    CommandLine cmd;
    cmd.AddValue("simTime", "Simulation time", simTime);
    cmd.AddValue("seed", "Random seed", seed);
    cmd.AddValue("outputDir", "Output directory", outputDir);
    cmd.AddValue("offeredLoadMbps", "Per-flow offered UDP load in Mbps", offeredLoadMbps);
    cmd.AddValue("packetSize", "UDP packet size in bytes", packetSize);
    cmd.AddValue("mobilitySpeed", "CPE random-walk speed in m/s", mobilitySpeed);
    cmd.AddValue("lifiRateMbps", "LiFi surrogate CSMA data rate in Mbps", lifiRateMbps);
    cmd.Parse(argc, argv);

    RngSeedManager::SetSeed(seed);

    NodeContainer cpes;
    cpes.Create(3);
    NodeContainer wifiAp;
    wifiAp.Create(1);
    NodeContainer lifiAp;
    lifiAp.Create(1);
    NodeContainer enb;
    enb.Create(1);
    
    NodeContainer remoteHostLte;
    remoteHostLte.Create(1);
    NodeContainer remoteHostWifi;
    remoteHostWifi.Create(1);
    NodeContainer remoteHostLifi;
    remoteHostLifi.Create(1);

    InternetStackHelper internet;
    internet.Install(cpes);
    internet.Install(wifiAp);
    internet.Install(lifiAp);
    internet.Install(remoteHostLte);
    internet.Install(remoteHostWifi);
    internet.Install(remoteHostLifi);

    MobilityHelper cpeMobility;
    cpeMobility.SetPositionAllocator("ns3::RandomRectanglePositionAllocator",
                                     "X", StringValue("ns3::UniformRandomVariable[Min=0.0|Max=50.0]"),
                                     "Y", StringValue("ns3::UniformRandomVariable[Min=0.0|Max=50.0]"));
    cpeMobility.SetMobilityModel("ns3::RandomWalk2dMobilityModel",
                                 "Bounds", RectangleValue(Rectangle(0.0, 50.0, 0.0, 50.0)),
                                 "Speed", StringValue("ns3::ConstantRandomVariable[Constant=" + std::to_string(mobilitySpeed) + "]"));
    cpeMobility.Install(cpes);

    Ptr<ListPositionAllocator> apPos = CreateObject<ListPositionAllocator>();
    apPos->Add(Vector(15.0, 25.0, 0.0));
    MobilityHelper apMobility;
    apMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    apMobility.SetPositionAllocator(apPos);
    apMobility.Install(wifiAp);

    Ptr<ListPositionAllocator> lifiPos = CreateObject<ListPositionAllocator>();
    lifiPos->Add(Vector(35.0, 25.0, 0.0));
    MobilityHelper lifiMobility;
    lifiMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    lifiMobility.SetPositionAllocator(lifiPos);
    lifiMobility.Install(lifiAp);

    Ptr<ListPositionAllocator> enbPos = CreateObject<ListPositionAllocator>();
    enbPos->Add(Vector(25.0, 25.0, 0.0));
    MobilityHelper enbMobility;
    enbMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    enbMobility.SetPositionAllocator(enbPos);
    enbMobility.Install(enb);

    MobilityHelper hostMobility;
    hostMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    hostMobility.Install(remoteHostLte);
    hostMobility.Install(remoteHostWifi);
    hostMobility.Install(remoteHostLifi);

    PointToPointHelper p2p;
    p2p.SetDeviceAttribute("DataRate", StringValue("1Gbps"));
    p2p.SetChannelAttribute("Delay", StringValue("2ms"));
    Ipv4AddressHelper ipv4;

    NetDeviceContainer wifiP2pDevs = p2p.Install(remoteHostWifi.Get(0), wifiAp.Get(0));
    ipv4.SetBase("192.168.1.0", "255.255.255.0");
    Ipv4InterfaceContainer wifiP2pIfaces = ipv4.Assign(wifiP2pDevs);

    NetDeviceContainer lifiP2pDevs = p2p.Install(remoteHostLifi.Get(0), lifiAp.Get(0));
    ipv4.SetBase("192.168.3.0", "255.255.255.0");
    Ipv4InterfaceContainer lifiP2pIfaces = ipv4.Assign(lifiP2pDevs);

    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211n);
    YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
    YansWifiPhyHelper wifiPhy;
    wifiPhy.SetChannel(wifiChannel.Create());
    WifiMacHelper wifiMac;
    Ssid ssid = Ssid("wifi-hybrid");

    wifiMac.SetType("ns3::ApWifiMac", "Ssid", SsidValue(ssid));
    NetDeviceContainer apWifiDevs = wifi.Install(wifiPhy, wifiMac, wifiAp);

    wifiMac.SetType("ns3::StaWifiMac", "Ssid", SsidValue(ssid));
    NetDeviceContainer staWifiDevs = wifi.Install(wifiPhy, wifiMac, cpes);

    ipv4.SetBase("192.168.2.0", "255.255.255.0");
    Ipv4InterfaceContainer apWifiIfaces = ipv4.Assign(apWifiDevs);
    Ipv4InterfaceContainer staWifiIfaces = ipv4.Assign(staWifiDevs);

    CsmaHelper csma;
    csma.SetChannelAttribute("DataRate", StringValue(std::to_string(lifiRateMbps) + "Mbps"));
    csma.SetChannelAttribute("Delay", TimeValue(NanoSeconds(10)));
    NodeContainer lifiNodes;
    lifiNodes.Add(lifiAp);
    lifiNodes.Add(cpes);
    NetDeviceContainer lifiDevs = csma.Install(lifiNodes);

    ipv4.SetBase("192.168.4.0", "255.255.255.0");
    Ipv4InterfaceContainer lifiIfaces = ipv4.Assign(lifiDevs);

    Ptr<LteHelper> lteHelper = CreateObject<LteHelper>();
    Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper>();
    lteHelper->SetEpcHelper(epcHelper);

    Ptr<Node> pgw = epcHelper->GetPgwNode();
    NetDeviceContainer lteP2pDevs = p2p.Install(pgw, remoteHostLte.Get(0));
    ipv4.SetBase("10.0.0.0", "255.0.0.0");
    Ipv4InterfaceContainer lteP2pIfaces = ipv4.Assign(lteP2pDevs);

    NetDeviceContainer enbDevs = lteHelper->InstallEnbDevice(enb);
    NetDeviceContainer ueLteDevs = lteHelper->InstallUeDevice(cpes);
    Ipv4InterfaceContainer ueLteIfaces = epcHelper->AssignUeIpv4Address(NetDeviceContainer(ueLteDevs));

    for (uint32_t i = 0; i < cpes.GetN(); ++i) {
        lteHelper->Attach(ueLteDevs.Get(i), enbDevs.Get(0));
    }

    Ipv4StaticRoutingHelper routingHelper;
    Ptr<Ipv4StaticRouting> wifiRouting = routingHelper.GetStaticRouting(remoteHostWifi.Get(0)->GetObject<Ipv4>());
    wifiRouting->AddNetworkRouteTo(Ipv4Address("192.168.2.0"), Ipv4Mask("255.255.255.0"), 1);

    Ptr<Ipv4StaticRouting> lifiRouting = routingHelper.GetStaticRouting(remoteHostLifi.Get(0)->GetObject<Ipv4>());
    lifiRouting->AddNetworkRouteTo(Ipv4Address("192.168.4.0"), Ipv4Mask("255.255.255.0"), 1);

    Ptr<Ipv4StaticRouting> lteRouting = routingHelper.GetStaticRouting(remoteHostLte.Get(0)->GetObject<Ipv4>());
    lteRouting->AddNetworkRouteTo(Ipv4Address("7.0.0.0"), Ipv4Mask("255.0.0.0"), 1);

    uint16_t port = 9;
    for (uint32_t i = 0; i < cpes.GetN(); ++i) {
        UdpServerHelper server(port);
        ApplicationContainer serverApp = server.Install(cpes.Get(i));
        serverApp.Start(Seconds(0.0));
        serverApp.Stop(Seconds(simTime));

        UdpClientHelper wifiClient(staWifiIfaces.GetAddress(i), port);
        wifiClient.SetAttribute("MaxPackets", UintegerValue(1000000));
        wifiClient.SetAttribute("Interval", TimeValue(Seconds(packetSize * 8.0 / (offeredLoadMbps * 1000000.0))));
        wifiClient.SetAttribute("PacketSize", UintegerValue(packetSize));
        ApplicationContainer wifiApp = wifiClient.Install(remoteHostWifi.Get(0));
        wifiApp.Start(Seconds(1.0));
        wifiApp.Stop(Seconds(simTime));

        UdpClientHelper lifiClient(lifiIfaces.GetAddress(i + 1), port);
        lifiClient.SetAttribute("MaxPackets", UintegerValue(1000000));
        lifiClient.SetAttribute("Interval", TimeValue(Seconds(packetSize * 8.0 / (offeredLoadMbps * 1000000.0))));
        lifiClient.SetAttribute("PacketSize", UintegerValue(packetSize));
        ApplicationContainer lifiApp = lifiClient.Install(remoteHostLifi.Get(0));
        lifiApp.Start(Seconds(1.0));
        lifiApp.Stop(Seconds(simTime));

        UdpClientHelper lteClient(ueLteIfaces.GetAddress(i), port);
        lteClient.SetAttribute("MaxPackets", UintegerValue(1000000));
        lteClient.SetAttribute("Interval", TimeValue(Seconds(packetSize * 8.0 / (offeredLoadMbps * 1000000.0))));
        lteClient.SetAttribute("PacketSize", UintegerValue(packetSize));
        ApplicationContainer lteApp = lteClient.Install(remoteHostLte.Get(0));
        lteApp.Start(Seconds(1.0));
        lteApp.Stop(Seconds(simTime));
    }

    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll();

    Simulator::Stop(Seconds(simTime));
    Simulator::Run();

    monitor->CheckForLostPackets();
    monitor->SerializeToXmlFile(outputDir + "/flowmon.xml", true, true);

    std::ofstream kpiFile;
    kpiFile.open(outputDir + "/kpi.csv");
    kpiFile << "flow_id,tx_packets,rx_packets,lost_packets,throughput_mbps,mean_delay_ms,mean_jitter_ms\n";

    Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmon.GetClassifier());
    std::map<FlowId, FlowMonitor::FlowStats> stats = monitor->GetFlowStats();
    for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin(); i != stats.end(); ++i) {
        double duration = i->second.timeLastRxPacket.GetSeconds() - i->second.timeFirstTxPacket.GetSeconds();
        if (duration <= 0.0) {
            duration = (simTime > 1.0) ? (simTime - 1.0) : simTime;
        }
        double throughput = (i->second.rxBytes * 8.0) / duration / 1000000.0;
        double meanDelay = (i->second.rxPackets > 0) ? (i->second.delaySum.GetSeconds() * 1000.0 / i->second.rxPackets) : 0.0;
        double meanJitter = (i->second.rxPackets > 1) ? (i->second.jitterSum.GetSeconds() * 1000.0 / (i->second.rxPackets - 1)) : 0.0;

        kpiFile << i->first << ","
                << i->second.txPackets << ","
                << i->second.rxPackets << ","
                << i->second.lostPackets << ","
                << throughput << ","
                << meanDelay << ","
                << meanJitter << "\n";
    }
    kpiFile.close();

    Simulator::Destroy();
    return 0;
}
