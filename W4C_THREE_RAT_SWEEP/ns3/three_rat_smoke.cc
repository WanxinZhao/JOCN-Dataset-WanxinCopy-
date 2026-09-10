/*
 * W4C three-RAT implementation and bounded-sweep executable.
 *
 * This file is intentionally separate from the validated legacy sweep.  It
 * instantiates CTTC 5G-LENA NR, native ns-3 Wi-Fi 802.11ax, and a small
 * equation-driven LOS LiFi/OWC receive-error model in one scenario.  The
 * LiFi packet-access path uses stock PointToPointNetDevice only as an IP/UDP
 * abstraction; packet corruption is decided by the optical equations in
 * lifi_owc.cc.  It is not a standardized LiFi PHY/MAC.
 */

#include "ns3/address-utils.h"
#include "ns3/antenna-module.h"
#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/nr-mac-scheduler-tdma-rr.h"
#include "ns3/nr-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/wifi-module.h"

#include "lifi_owc.h"

#include <algorithm>
#include <fstream>
#include <iomanip>
#include <map>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

// The implementation is included into this single scratch translation unit
// so that the W4C source remains project-local without changing the legacy
// ns-3 build graph.
#include "lifi_owc_impl.inc"

using namespace ns3;

namespace
{

struct AppFlow
{
    std::string branch;
    uint32_t cpe;
    Ptr<Node> sourceNode;
    Ptr<Node> destinationNode;
    Ipv4Address source;
    Ipv4Address destination;
    uint16_t sourcePort;
    uint16_t destinationPort;
};

std::string
FlowKey(const Ipv4Address& source,
        const Ipv4Address& destination,
        uint16_t sourcePort,
        uint16_t destinationPort,
        uint8_t protocol)
{
    std::ostringstream out;
    out << source << ':' << sourcePort << '-' << destination << ':' << destinationPort << '-'
        << static_cast<uint32_t>(protocol);
    return out.str();
}

LiFiParameters
MakeLiFiParameters(double txPowerW,
                   double halfPowerDeg,
                   double detectorAreaM2,
                   double responsivityAperW,
                   double fovDeg,
                   double concentratorIndex,
                   double filterGain,
                   double backgroundCurrentA,
                   double bandwidthHz,
                   double temperatureK,
                   double loadResistanceOhm,
                   uint32_t packetBytes,
                   double rateMbps,
                   const Vector& txOrientation,
                   const Vector& rxOrientation)
{
    LiFiParameters p;
    p.txPowerW = txPowerW;
    p.halfPowerSemiAngleRad = halfPowerDeg * 3.14159265358979323846 / 180.0;
    p.detectorAreaM2 = detectorAreaM2;
    p.responsivityAperW = responsivityAperW;
    p.concentratorIndex = concentratorIndex;
    p.opticalFilterGain = filterGain;
    p.backgroundCurrentA = backgroundCurrentA;
    p.bandwidthHz = bandwidthHz;
    p.temperatureK = temperatureK;
    p.loadResistanceOhm = loadResistanceOhm;
    p.packetBytes = packetBytes;
    p.nominalRateBps = rateMbps * 1.0e6;
    p.receiverFovRad = fovDeg * 3.14159265358979323846 / 180.0;
    p.txOrientation = txOrientation;
    p.rxOrientation = rxOrientation;
    return p;
}

void
InstallCpeMobility(const NodeContainer& cpes, double speed)
{
    Ptr<ListPositionAllocator> positions = CreateObject<ListPositionAllocator>();
    positions->Add(Vector(24.0, 25.0, 1.0));
    positions->Add(Vector(25.0, 25.0, 1.0));
    positions->Add(Vector(26.0, 25.0, 1.0));

    MobilityHelper mobility;
    mobility.SetPositionAllocator(positions);
    mobility.SetMobilityModel(
        "ns3::RandomWalk2dMobilityModel",
        "Mode",
        StringValue("Time"),
        "Time",
        TimeValue(Seconds(0.25)),
        "Speed",
        StringValue("ns3::ConstantRandomVariable[Constant=" + std::to_string(speed) + "]"),
        "Bounds",
        RectangleValue(Rectangle(0.0, 50.0, 0.0, 50.0)));
    mobility.Install(cpes);
}

void
InstallFixedMobility(const Ptr<Node>& node, const Vector& position)
{
    MobilityHelper mobility;
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(node);
    node->GetObject<MobilityModel>()->SetPosition(position);
}

Ptr<LiFiStateLogger>
InstallLiFiLinks(const Ptr<Node>& ap,
                const NodeContainer& cpes,
                const LiFiParameters& parameters,
                const std::string& outputDir,
                double p2pRateMbps,
                double offeredMbps,
                Time appStart,
                Time appStop,
                std::vector<AppFlow>* flows,
                uint16_t portBase)
{
    Ptr<LiFiStateLogger> logger =
        Create<LiFiStateLogger>(outputDir + "/optical_state.csv", 0.1);
    for (uint32_t i = 0; i < cpes.GetN(); ++i)
    {
        PointToPointHelper p2p;
        p2p.SetDeviceAttribute("DataRate", DataRateValue(DataRate(p2pRateMbps * 1.0e6)));
        p2p.SetChannelAttribute("Delay", TimeValue(NanoSeconds(10)));
        NetDeviceContainer devices = p2p.Install(ap, cpes.Get(i));

        Ptr<LiFiErrorModel> error = CreateObject<LiFiErrorModel>();
        error->SetParameters(parameters);
        error->SetGeometry(ap->GetObject<MobilityModel>(),
                           cpes.Get(i)->GetObject<MobilityModel>(),
                           parameters.txOrientation,
                           parameters.rxOrientation,
                           i + 1);
        error->SetLogger(logger);
        error->AssignStreams(1000 + i);
        DynamicCast<PointToPointNetDevice>(devices.Get(1))->SetReceiveErrorModel(error);

        Ipv4AddressHelper addresses;
        const std::string base = "10.30." + std::to_string(i) + ".0";
        addresses.SetBase(Ipv4Address(base.c_str()), Ipv4Mask("255.255.255.252"));
        Ipv4InterfaceContainer interfaces = addresses.Assign(devices);

        const uint16_t port = portBase + static_cast<uint16_t>(i);
        UdpServerHelper server(port);
        ApplicationContainer serverApps = server.Install(cpes.Get(i));
        serverApps.Start(appStart);
        serverApps.Stop(appStop);
        UdpClientHelper client(interfaces.GetAddress(1), port);
        client.SetAttribute("MaxPackets", UintegerValue(1000000));
        client.SetAttribute("PacketSize", UintegerValue(parameters.packetBytes));
        client.SetAttribute("Interval",
                            TimeValue(Seconds(8.0 * parameters.packetBytes /
                                              (offeredMbps * 1.0e6))));
        ApplicationContainer clientApps = client.Install(ap);
        clientApps.Start(appStart);
        clientApps.Stop(appStop);
        if (flows)
        {
            flows->push_back({"LiFi", i + 1, ap, cpes.Get(i), interfaces.GetAddress(0),
                              interfaces.GetAddress(1), static_cast<uint16_t>(49153 + i), port});
        }
    }
    return logger;
}

void
WriteScenarioMetadata(const std::string& path, const std::vector<AppFlow>& flows)
{
    std::ofstream out(path, std::ios::out | std::ios::trunc);
    NS_ABORT_MSG_IF(!out.is_open(), "Cannot open scenario metadata: " << path);
    out << "branch,cpe_id,source_ip,destination_ip,source_port,destination_port,protocol\n";
    for (const auto& f : flows)
    {
        out << f.branch << ',' << f.cpe << ',' << f.source << ',' << f.destination << ','
            << f.sourcePort << ',' << f.destinationPort << ",UDP\n";
    }
}

void
WriteKpis(const std::string& path,
          const std::vector<AppFlow>& flows,
          Ptr<FlowMonitor> monitor,
          Ptr<Ipv4FlowClassifier> classifier)
{
    std::map<std::string, AppFlow> expected;
    for (const auto& f : flows)
    {
        expected[FlowKey(f.source, f.destination, f.sourcePort, f.destinationPort, 17)] = f;
    }
    std::ofstream out(path, std::ios::out | std::ios::trunc);
    NS_ABORT_MSG_IF(!out.is_open(), "Cannot open KPI output: " << path);
    out << "flow_id,branch,cpe_id,source_ip,destination_ip,source_port,destination_port,"
           "tx_packets,rx_packets,lost_packets,rx_bytes,first_tx_s,last_rx_s,duration_s,"
           "throughput_mbps,mean_delay_ms,mean_jitter_ms,flowmonitor_loss_ratio,mapping_status\n";
    for (const auto& item : monitor->GetFlowStats())
    {
        const FlowId flowId = item.first;
        const FlowMonitor::FlowStats& s = item.second;
        const Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(flowId);
        const std::string key = FlowKey(t.sourceAddress, t.destinationAddress, t.sourcePort,
                                         t.destinationPort, t.protocol);
        auto match = expected.find(key);
        if (match == expected.end())
        {
            continue; // infrastructure/control flows are not application rows
        }
        const double firstTx = s.timeFirstTxPacket.GetSeconds();
        const double lastRx = s.timeLastRxPacket.GetSeconds();
        const double duration = lastRx > firstTx ? lastRx - firstTx : 0.0;
        const double throughput = duration > 0.0 ? 8.0 * s.rxBytes / duration / 1.0e6 : 0.0;
        const double delay = s.rxPackets > 0 ? s.delaySum.GetSeconds() * 1000.0 / s.rxPackets : 0.0;
        const double jitter = s.rxPackets > 1
                                  ? s.jitterSum.GetSeconds() * 1000.0 / (s.rxPackets - 1)
                                  : 0.0;
        const double loss = s.txPackets > 0 ? static_cast<double>(s.lostPackets) / s.txPackets : 0.0;
        const AppFlow& f = match->second;
        out << flowId << ',' << f.branch << ',' << f.cpe << ',' << f.source << ',' << f.destination
            << ',' << f.sourcePort << ',' << f.destinationPort << ',' << s.txPackets << ','
            << s.rxPackets << ',' << s.lostPackets << ',' << s.rxBytes << ',' << std::setprecision(17)
            << firstTx << ',' << lastRx << ',' << duration << ',' << throughput << ',' << delay << ','
            << jitter << ',' << loss << ",EXPECTED\n";
    }
}

uint32_t
WriteFlowMapping(const std::string& path,
                 const std::vector<AppFlow>& flows,
                 Ptr<FlowMonitor> monitor,
                 Ptr<Ipv4FlowClassifier> classifier)
{
    std::map<std::string, AppFlow> expected;
    for (const auto& f : flows)
    {
        expected[FlowKey(f.source, f.destination, f.sourcePort, f.destinationPort, 17)] = f;
    }
    std::ofstream out(path, std::ios::out | std::ios::trunc);
    NS_ABORT_MSG_IF(!out.is_open(), "Cannot open flow mapping output: " << path);
    out << "flow_id,branch,cpe_id,source_ip,destination_ip,source_port,destination_port,"
           "source_ipv4_interface,destination_ipv4_interface,source_device,destination_device,"
           "mapping_status,interface_route_status\n";
    uint32_t matched = 0;
    for (const auto& item : monitor->GetFlowStats())
    {
        const auto tuple = classifier->FindFlow(item.first);
        const std::string key = FlowKey(tuple.sourceAddress, tuple.destinationAddress,
                                         tuple.sourcePort, tuple.destinationPort, tuple.protocol);
        auto match = expected.find(key);
        if (match == expected.end())
        {
            continue;
        }
        ++matched;
        const auto& f = match->second;
        const int32_t sourceInterface = f.sourceNode->GetObject<Ipv4>()->GetInterfaceForAddress(f.source);
        const int32_t destinationInterface =
            f.destinationNode->GetObject<Ipv4>()->GetInterfaceForAddress(f.destination);
        NS_ABORT_MSG_IF(sourceInterface < 0 || destinationInterface < 0,
                        "Application address is not bound to the expected endpoint node");
        const std::string sourceDevice =
            f.sourceNode->GetObject<Ipv4>()->GetNetDevice(sourceInterface)->GetInstanceTypeId().GetName();
        const std::string destinationDevice =
            f.destinationNode->GetObject<Ipv4>()->GetNetDevice(destinationInterface)
                ->GetInstanceTypeId()
                .GetName();
        const auto has = [](const std::string& value, const std::string& token) {
            return value.find(token) != std::string::npos;
        };
        bool interfaceOk = false;
        if (f.branch == "NR")
        {
            interfaceOk = has(sourceDevice, "PointToPointNetDevice") &&
                          has(destinationDevice, "NrUeNetDevice");
        }
        else if (f.branch == "WiFi80211ax")
        {
            interfaceOk = has(sourceDevice, "WifiNetDevice") && has(destinationDevice, "WifiNetDevice");
        }
        else if (f.branch == "LiFi")
        {
            interfaceOk = has(sourceDevice, "PointToPointNetDevice") &&
                          has(destinationDevice, "PointToPointNetDevice");
        }
        out << item.first << ',' << f.branch << ',' << f.cpe << ',' << f.source << ','
            << f.destination << ',' << f.sourcePort << ',' << f.destinationPort << ','
            << sourceInterface << ',' << destinationInterface << ',' << sourceDevice << ','
            << destinationDevice << ",MATCHED," << (interfaceOk ? "PASS" : "FAIL") << '\n';
        NS_ABORT_MSG_IF(!interfaceOk, "Application flow resolved to an unexpected access device");
    }
    return matched;
}

void
WriteRunConfig(const std::string& path,
               const std::string& mode,
               double simSeconds,
               double speed,
               double offeredMbps,
               Time appStart,
               Time appStop,
               uint32_t seed,
               uint64_t run,
               const LiFiParameters& lifi)
{
    std::ofstream out(path, std::ios::out | std::ios::trunc);
    out << "key,value,unit\n"
        << "mode," << mode << ",\n"
        << "ns3_version,3.44,\n"
        << "nr_backend,CTTC 5G-LENA 5g-lena-v4.0.y,\n"
        << "wifi_backend,WIFI_STANDARD_80211ax,\n"
        << "lifi_backend,equation-driven LOS LiFi/OWC,\n"
        << "simulation_duration," << simSeconds << ",s\n"
        << "mobility_speed," << speed << ",m/s\n"
        << "offered_load," << offeredMbps << ",Mbps\n"
        << "application_start," << appStart.GetSeconds() << ",s\n"
        << "application_stop," << appStop.GetSeconds() << ",s\n"
        << "lifi_receiver_fov_deg," << lifi.receiverFovRad * 180.0 / 3.14159265358979323846
        << ",degree\n"
        << "random_seed," << seed << ",\n"
        << "run_number," << run << ",\n"
        << "lifi_tx_power," << lifi.txPowerW << ",W\n"
        << "lifi_half_power_semi_angle," << lifi.halfPowerSemiAngleRad << ",rad\n"
        << "lifi_detector_area," << lifi.detectorAreaM2 << ",m^2\n"
        << "lifi_responsivity," << lifi.responsivityAperW << ",A/W\n"
        << "lifi_receiver_fov," << lifi.receiverFovRad << ",rad\n"
        << "lifi_concentrator_index," << lifi.concentratorIndex << ",1\n"
        << "lifi_filter_gain," << lifi.opticalFilterGain << ",1\n"
        << "lifi_background_current," << lifi.backgroundCurrentA << ",A\n"
        << "lifi_bandwidth," << lifi.bandwidthHz << ",Hz\n"
        << "lifi_temperature," << lifi.temperatureK << ",K\n"
        << "lifi_load_resistance," << lifi.loadResistanceOhm << ",ohm\n"
        << "packet_size," << lifi.packetBytes << ",bytes\n"
        << "lifi_nominal_rate," << lifi.nominalRateBps << ",bit/s\n";
    out << "tx_orientation," << lifi.txOrientation.x << ";" << lifi.txOrientation.y << ";"
        << lifi.txOrientation.z << ",unit_vector\n"
        << "rx_orientation," << lifi.rxOrientation.x << ";" << lifi.rxOrientation.y << ";"
        << lifi.rxOrientation.z << ",unit_vector\n";
}

uint32_t
RunLifiOnly(const std::string& outputDir,
            Time simTime,
            double speed,
            const LiFiParameters& parameters,
            double offeredMbps,
            Time appStart,
            Time appStop,
            uint32_t seed,
            uint64_t run)
{
    RngSeedManager::SetSeed(seed);
    RngSeedManager::SetRun(run);
    NodeContainer ap;
    ap.Create(1);
    NodeContainer cpes;
    cpes.Create(3);
    InstallFixedMobility(ap.Get(0), Vector(25.0, 25.0, 3.0));
    InstallCpeMobility(cpes, speed);

    InternetStackHelper internet;
    internet.Install(ap);
    internet.Install(cpes);

    std::vector<AppFlow> flows;
    InstallLiFiLinks(ap.Get(0), cpes, parameters, outputDir, parameters.nominalRateBps / 1.0e6,
                     offeredMbps, appStart, appStop, &flows, 6000);
    WriteScenarioMetadata(outputDir + "/scenario_metadata.csv", flows);
    WriteRunConfig(outputDir + "/run_config.csv", "lifi-only", simTime.GetSeconds(), speed,
                   offeredMbps, appStart, appStop, seed, run, parameters);

    FlowMonitorHelper flowmonHelper;
    Ptr<FlowMonitor> monitor = flowmonHelper.InstallAll();
    Simulator::Stop(simTime);
    Simulator::Run();
    monitor->CheckForLostPackets();
    monitor->SerializeToXmlFile(outputDir + "/flowmon.xml", true, true);
    Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmonHelper.GetClassifier());
    WriteKpis(outputDir + "/kpi.csv", flows, monitor, classifier);
    const uint32_t matched = WriteFlowMapping(outputDir + "/flow_mapping.csv", flows, monitor, classifier);
    Simulator::Destroy();
    return matched;
}

uint32_t
RunIntegrated(const std::string& outputDir,
              Time simTime,
              double speed,
              const LiFiParameters& parameters,
              double offeredMbps,
              Time appStart,
              Time appStop,
              uint32_t seed,
              uint64_t run)
{
    RngSeedManager::SetSeed(seed);
    RngSeedManager::SetRun(run);
    Config::SetDefault("ns3::NrRlcUm::MaxTxBufferSize", UintegerValue(999999999));
    NodeContainer cpes;
    cpes.Create(3);
    NodeContainer gnb;
    gnb.Create(1);
    NodeContainer wifiAp;
    wifiAp.Create(1);
    NodeContainer lifiAp;
    lifiAp.Create(1);
    InstallCpeMobility(cpes, speed);
    InstallFixedMobility(gnb.Get(0), Vector(25.0, 25.0, 3.0));
    InstallFixedMobility(wifiAp.Get(0), Vector(25.0, 25.0, 2.5));
    InstallFixedMobility(lifiAp.Get(0), Vector(25.0, 25.0, 3.0));

    Ptr<NrPointToPointEpcHelper> nrEpcHelper = CreateObject<NrPointToPointEpcHelper>();
    Ptr<IdealBeamformingHelper> beamforming = CreateObject<IdealBeamformingHelper>();
    Ptr<NrHelper> nrHelper = CreateObject<NrHelper>();
    nrHelper->SetBeamformingHelper(beamforming);
    nrHelper->SetEpcHelper(nrEpcHelper);
    nrHelper->SetSchedulerTypeId(NrMacSchedulerTdmaRR::GetTypeId());

    const double frequency = 3.5e9;
    const double bandwidth = 40e6;
    CcBwpCreator creator;
    CcBwpCreator::SimpleOperationBandConf bandConf(frequency, bandwidth, 1);
    OperationBandInfo band = creator.CreateOperationBandContiguousCc(bandConf);
    Ptr<NrChannelHelper> channelHelper = CreateObject<NrChannelHelper>();
    channelHelper->ConfigureFactories("InH-OfficeOpen", "Default", "ThreeGpp");
    channelHelper->SetChannelConditionModelAttribute("UpdatePeriod", TimeValue(MilliSeconds(0)));
    channelHelper->AssignChannelsToBands({band});
    BandwidthPartInfoPtrVector allBwps = CcBwpCreator::GetAllBwps({band});
    beamforming->SetAttribute("BeamformingMethod",
                              TypeIdValue(DirectPathBeamforming::GetTypeId()));
    nrHelper->SetUeAntennaAttribute("NumRows", UintegerValue(2));
    nrHelper->SetUeAntennaAttribute("NumColumns", UintegerValue(2));
    nrHelper->SetUeAntennaAttribute("AntennaElement",
                                    PointerValue(CreateObject<IsotropicAntennaModel>()));
    nrHelper->SetGnbAntennaAttribute("NumRows", UintegerValue(4));
    nrHelper->SetGnbAntennaAttribute("NumColumns", UintegerValue(4));
    nrHelper->SetGnbAntennaAttribute("AntennaElement",
                                     PointerValue(CreateObject<IsotropicAntennaModel>()));

    NetDeviceContainer gnbDevices = nrHelper->InstallGnbDevice(gnb, allBwps);
    NetDeviceContainer ueDevices = nrHelper->InstallUeDevice(cpes, allBwps);
    nrHelper->GetGnbPhy(gnbDevices.Get(0), 0)->SetAttribute("Numerology", UintegerValue(1));
    nrHelper->GetGnbPhy(gnbDevices.Get(0), 0)->SetTxPower(30.0);
    nrHelper->AssignStreams(gnbDevices, 10);
    nrHelper->AssignStreams(ueDevices, 100);

    auto [remoteHost, pgwAddress] =
        nrEpcHelper->SetupRemoteHost("100Gb/s", 2500, Seconds(0.001));
    InternetStackHelper internet;
    internet.Install(cpes);
    internet.Install(wifiAp);
    internet.Install(lifiAp);
    Ipv4InterfaceContainer ueIp = nrEpcHelper->AssignUeIpv4Address(ueDevices);
    nrHelper->AttachToClosestGnb(ueDevices, gnbDevices);
    // SetupRemoteHost returns the PGW-side address; the UDP source is the
    // remote-host side of the point-to-point backhaul (interface index 1).
    const Ipv4Address remoteHostAddress =
        remoteHost->GetObject<Ipv4>()->GetAddress(1, 0).GetLocal();

    std::vector<AppFlow> flows;
    for (uint32_t i = 0; i < cpes.GetN(); ++i)
    {
        const uint16_t port = 4000 + static_cast<uint16_t>(i);
        UdpServerHelper server(port);
        ApplicationContainer serverApps = server.Install(cpes.Get(i));
        serverApps.Start(appStart);
        serverApps.Stop(appStop);
        UdpClientHelper client(ueIp.GetAddress(i), port);
        client.SetAttribute("MaxPackets", UintegerValue(1000000));
        client.SetAttribute("PacketSize", UintegerValue(parameters.packetBytes));
        client.SetAttribute("Interval", TimeValue(Seconds(8.0 * parameters.packetBytes / (offeredMbps * 1.0e6))));
        ApplicationContainer clientApps = client.Install(remoteHost);
        clientApps.Start(appStart);
        clientApps.Stop(appStop);
        flows.push_back({"NR", i + 1, remoteHost, cpes.Get(i), remoteHostAddress, ueIp.GetAddress(i),
                         static_cast<uint16_t>(49153 + i), port});
    }

    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211ax);
    wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                 "DataMode",
                                 StringValue("HeMcs0"),
                                 "ControlMode",
                                 StringValue("OfdmRate6Mbps"));
    WifiMacHelper mac;
    Ssid ssid = Ssid("w4b-80211ax");
    mac.SetType("ns3::StaWifiMac", "Ssid", SsidValue(ssid), "ActiveProbing", BooleanValue(false));
    YansWifiChannelHelper channel = YansWifiChannelHelper::Default();
    YansWifiPhyHelper phy;
    phy.SetChannel(channel.Create());
    phy.Set("ChannelSettings", StringValue("{0, 20, BAND_5GHZ, 0}"));
    phy.Set("TxPowerStart", DoubleValue(16.0));
    phy.Set("TxPowerEnd", DoubleValue(16.0));
    NetDeviceContainer staDevices = wifi.Install(phy, mac, cpes);
    mac.SetType("ns3::ApWifiMac", "Ssid", SsidValue(ssid));
    NetDeviceContainer apDevice = wifi.Install(phy, mac, wifiAp);
    Ipv4AddressHelper wifiAddress;
    wifiAddress.SetBase("10.20.0.0", "255.255.255.0");
    Ipv4InterfaceContainer wifiApIp = wifiAddress.Assign(apDevice);
    Ipv4InterfaceContainer staIp = wifiAddress.Assign(staDevices);
    for (uint32_t i = 0; i < cpes.GetN(); ++i)
    {
        const uint16_t port = 5000 + static_cast<uint16_t>(i);
        UdpServerHelper server(port);
        ApplicationContainer serverApps = server.Install(cpes.Get(i));
        serverApps.Start(appStart);
        serverApps.Stop(appStop);
        UdpClientHelper client(staIp.GetAddress(i), port);
        client.SetAttribute("MaxPackets", UintegerValue(1000000));
        client.SetAttribute("PacketSize", UintegerValue(parameters.packetBytes));
        client.SetAttribute("Interval", TimeValue(Seconds(8.0 * parameters.packetBytes / (offeredMbps * 1.0e6))));
        ApplicationContainer clientApps = client.Install(wifiAp.Get(0));
        clientApps.Start(appStart);
        clientApps.Stop(appStop);
        flows.push_back({"WiFi80211ax", i + 1, wifiAp.Get(0), cpes.Get(i), wifiApIp.GetAddress(0),
                         staIp.GetAddress(i),
                         static_cast<uint16_t>(49153 + i), port});
    }

    InstallLiFiLinks(lifiAp.Get(0), cpes, parameters, outputDir, parameters.nominalRateBps / 1.0e6,
                     offeredMbps, appStart, appStop, &flows, 6000);
    WriteScenarioMetadata(outputDir + "/scenario_metadata.csv", flows);
    WriteRunConfig(outputDir + "/run_config.csv", "integrated-three-rat", simTime.GetSeconds(), speed,
                   offeredMbps, appStart, appStop, seed, run, parameters);

    FlowMonitorHelper flowmonHelper;
    Ptr<FlowMonitor> monitor = flowmonHelper.InstallAll();
    Simulator::Stop(simTime);
    Simulator::Run();
    monitor->CheckForLostPackets();
    monitor->SerializeToXmlFile(outputDir + "/flowmon.xml", true, true);
    Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmonHelper.GetClassifier());
    WriteKpis(outputDir + "/kpi.csv", flows, monitor, classifier);
    const uint32_t matched = WriteFlowMapping(outputDir + "/flow_mapping.csv", flows, monitor, classifier);
    std::ofstream summary(outputDir + "/runtime_summary.csv", std::ios::out | std::ios::trunc);
    summary << "expected_application_flows,matched_flow_records\n" << flows.size() << ',' << matched << '\n';
    Simulator::Destroy();
    return matched;
}

void
WriteLinkProbe(const std::string& path, const LiFiParameters& parameters)
{
    struct Geometry
    {
        const char* name;
        Vector tx;
        Vector rx;
        Vector txNormal;
        Vector rxNormal;
    } geometries[] = {
        {"aligned_near", Vector(0, 0, 0), Vector(0, 0, 2), Vector(0, 0, 1), Vector(0, 0, -1)},
        {"aligned_far", Vector(0, 0, 0), Vector(0, 0, 4), Vector(0, 0, 1), Vector(0, 0, -1)},
        {"out_of_fov", Vector(0, 0, 0), Vector(0, 0, 2), Vector(0, 0, 1),
         Vector(std::sin(80.0 * 3.14159265358979323846 / 180.0), 0,
                -std::cos(80.0 * 3.14159265358979323846 / 180.0))}};
    std::ofstream out(path, std::ios::out | std::ios::trunc);
    out << "geometry,distance_m,irradiance_angle_rad,incidence_angle_rad,in_fov,h_los,"
           "received_optical_power_w,snr,ber,per\n";
    for (const auto& g : geometries)
    {
        const LiFiState state = LiFiLinkCalculator::Calculate(parameters, g.tx, g.rx, g.txNormal,
                                                               g.rxNormal, 0.0, 0);
        out << g.name << ',' << std::setprecision(17) << state.distanceM << ','
            << state.irradianceAngleRad << ',' << state.incidenceAngleRad << ','
            << (state.inFov ? 1 : 0) << ',' << state.hLos << ',' << state.receivedPowerW << ','
            << state.snr << ',' << state.ber << ',' << state.per << '\n';
    }
}

} // namespace

int
main(int argc, char* argv[])
{
    std::string mode = "integrated";
    std::string outputDir = "./w4c-output";
    Time simTime = Seconds(10.0);
    double speed = 0.5;
    double offeredMbps = 2.0;
    Time appStart = Seconds(1.0);
    Time appStop = Seconds(9.5);
    double txPowerW = 10.0;
    double halfPowerDeg = 60.0;
    double detectorAreaM2 = 1.0e-4;
    double responsivityAperW = 0.5;
    double fovDeg = 70.0;
    double concentratorIndex = 1.5;
    double filterGain = 1.0;
    double backgroundCurrentA = 5.1e-6;
    double bandwidthHz = 3.0e5;
    double temperatureK = 295.0;
    double loadResistanceOhm = 1.0e6;
    double txOrientationX = 0.0;
    double txOrientationY = 0.0;
    double txOrientationZ = -1.0;
    double rxOrientationX = 0.0;
    double rxOrientationY = 0.0;
    double rxOrientationZ = 1.0;
    uint32_t packetBytes = 1024;
    double lifiRateMbps = 100.0;
    uint32_t seed = 123;
    uint64_t run = 1;
    CommandLine cmd(__FILE__);
    cmd.AddValue("mode", "lifi-only, integrated, or link-probe", mode);
    cmd.AddValue("outputDir", "existing output directory", outputDir);
    cmd.AddValue("simTime", "bounded smoke duration", simTime);
    cmd.AddValue("speed", "CPE speed in m/s", speed);
    cmd.AddValue("offeredMbps", "common UDP offered load in Mbps", offeredMbps);
    cmd.AddValue("appStart", "application start time", appStart);
    cmd.AddValue("appStop", "application stop time", appStop);
    cmd.AddValue("txPowerW", "LiFi optical transmit power in W", txPowerW);
    cmd.AddValue("halfPowerDeg", "LED half-power semi-angle in degrees", halfPowerDeg);
    cmd.AddValue("detectorAreaM2", "photodetector area in square metres", detectorAreaM2);
    cmd.AddValue("responsivityAperW", "photodetector responsivity in A/W", responsivityAperW);
    cmd.AddValue("fovDeg", "LiFi receiver FOV in degrees", fovDeg);
    cmd.AddValue("concentratorIndex", "optical concentrator refractive index", concentratorIndex);
    cmd.AddValue("filterGain", "optical filter gain", filterGain);
    cmd.AddValue("backgroundCurrentA", "background current in A", backgroundCurrentA);
    cmd.AddValue("bandwidthHz", "electrical bandwidth in Hz", bandwidthHz);
    cmd.AddValue("temperatureK", "receiver temperature in K", temperatureK);
    cmd.AddValue("loadResistanceOhm", "load resistance in ohm", loadResistanceOhm);
    cmd.AddValue("txOrientationX", "transmitter orientation x component", txOrientationX);
    cmd.AddValue("txOrientationY", "transmitter orientation y component", txOrientationY);
    cmd.AddValue("txOrientationZ", "transmitter orientation z component", txOrientationZ);
    cmd.AddValue("rxOrientationX", "receiver orientation x component", rxOrientationX);
    cmd.AddValue("rxOrientationY", "receiver orientation y component", rxOrientationY);
    cmd.AddValue("rxOrientationZ", "receiver orientation z component", rxOrientationZ);
    cmd.AddValue("packetBytes", "UDP packet size in bytes", packetBytes);
    cmd.AddValue("lifiRateMbps", "nominal LiFi packet-link rate", lifiRateMbps);
    cmd.AddValue("seed", "ns-3 RNG seed", seed);
    cmd.AddValue("run", "ns-3 RNG run number", run);
    cmd.Parse(argc, argv);

    const LiFiParameters parameters =
        MakeLiFiParameters(txPowerW,
                           halfPowerDeg,
                           detectorAreaM2,
                           responsivityAperW,
                           fovDeg,
                           concentratorIndex,
                           filterGain,
                           backgroundCurrentA,
                           bandwidthHz,
                           temperatureK,
                           loadResistanceOhm,
                           packetBytes,
                           lifiRateMbps,
                           Vector(txOrientationX, txOrientationY, txOrientationZ),
                           Vector(rxOrientationX, rxOrientationY, rxOrientationZ));

    if (mode == "link-probe")
    {
        WriteLinkProbe(outputDir + "/lifi_link_probe.csv", parameters);
        return 0;
    }
    if (mode == "lifi-only")
    {
        return RunLifiOnly(outputDir, simTime, speed, parameters, offeredMbps, appStart, appStop, seed, run) == 3
                   ? 0
                   : 2;
    }
    if (mode == "integrated")
    {
        return RunIntegrated(outputDir, simTime, speed, parameters, offeredMbps, appStart, appStop, seed, run) == 9
                   ? 0
                   : 2;
    }
    std::cerr << "Unknown mode: " << mode << '\n';
    return 2;
}
