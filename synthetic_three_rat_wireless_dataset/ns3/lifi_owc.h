/*
 * W4B equation-driven LOS LiFi/OWC link model.
 *
 * This is intentionally a small link/error model, not a standardized LiFi
 * PHY/MAC.  It can be used behind a stock packet-access NetDevice while the
 * receive decision is driven by the optical link budget below.
 */
#ifndef W4B_LIFI_OWC_H
#define W4B_LIFI_OWC_H

#include "ns3/error-model.h"
#include "ns3/mobility-model.h"
#include "ns3/random-variable-stream.h"
#include "ns3/simple-ref-count.h"
#include "ns3/vector.h"

#include <fstream>
#include <map>
#include <string>

namespace ns3
{

struct LiFiParameters
{
    double txPowerW = 10.0;
    double halfPowerSemiAngleRad = 1.0471975511965976; // 60 deg
    double detectorAreaM2 = 1.0e-4;                    // 1 cm^2
    double responsivityAperW = 0.5;
    double receiverFovRad = 1.2217304763960306; // 70 deg
    double concentratorIndex = 1.5;
    double opticalFilterGain = 1.0;
    double backgroundCurrentA = 5.1e-6;
    double bandwidthHz = 3.0e5;
    double temperatureK = 295.0;
    double loadResistanceOhm = 1.0e6;
    uint32_t packetBytes = 1024;
    double nominalRateBps = 100.0e6;
    Vector txOrientation = Vector(0.0, 0.0, -1.0);
    Vector rxOrientation = Vector(0.0, 0.0, 1.0);
};

struct LiFiState
{
    double timeS = 0.0;
    uint32_t cpeId = 0;
    double distanceM = 0.0;
    double irradianceAngleRad = 0.0;
    double incidenceAngleRad = 0.0;
    bool inFov = false;
    double lambertianOrder = 0.0;
    double hLos = 0.0;
    double receivedPowerW = 0.0;
    double signalCurrentA = 0.0;
    double shotVarianceA2 = 0.0;
    double thermalVarianceA2 = 0.0;
    double snr = 0.0;
    double ber = 0.5;
    double per = 1.0;
};

class LiFiLinkCalculator
{
  public:
    static double LambertianOrder(double halfPowerSemiAngleRad);
    static LiFiState Calculate(const LiFiParameters& parameters,
                               const Vector& txPosition,
                               const Vector& rxPosition,
                               const Vector& txOrientation,
                               const Vector& rxOrientation,
                               double timeS,
                               uint32_t cpeId);
};

class LiFiStateLogger : public SimpleRefCount<LiFiStateLogger>
{
  public:
    LiFiStateLogger(const std::string& path, double samplePeriodS);
    ~LiFiStateLogger();
    void Log(const LiFiState& state, uint64_t packetCount, uint64_t corruptedPackets);

  private:
    std::ofstream m_stream;
    double m_samplePeriodS;
    std::map<uint32_t, double> m_lastSampleS;
};

class LiFiErrorModel : public ErrorModel
{
  public:
    static TypeId GetTypeId();
    LiFiErrorModel();
    ~LiFiErrorModel() override;

    void SetParameters(const LiFiParameters& parameters);
    void SetGeometry(Ptr<MobilityModel> transmitter,
                     Ptr<MobilityModel> receiver,
                     const Vector& txOrientation,
                     const Vector& rxOrientation,
                     uint32_t cpeId);
    void SetLogger(Ptr<LiFiStateLogger> logger);
    int64_t AssignStreams(int64_t stream);
    const LiFiState& GetLastState() const;

  private:
    bool DoCorrupt(Ptr<Packet> packet) override;
    void DoReset() override;

    LiFiParameters m_parameters;
    Ptr<MobilityModel> m_transmitter;
    Ptr<MobilityModel> m_receiver;
    Vector m_txOrientation;
    Vector m_rxOrientation;
    uint32_t m_cpeId;
    Ptr<UniformRandomVariable> m_uniform;
    Ptr<LiFiStateLogger> m_logger;
    LiFiState m_lastState;
    uint64_t m_packetCount;
    uint64_t m_corruptedPackets;
};

} // namespace ns3

#endif // W4B_LIFI_OWC_H
