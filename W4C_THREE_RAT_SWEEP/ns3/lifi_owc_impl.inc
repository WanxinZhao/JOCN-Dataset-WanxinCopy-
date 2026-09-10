#include "lifi_owc.h"

#include "ns3/log.h"
#include "ns3/packet.h"
#include "ns3/simulator.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace ns3
{

NS_LOG_COMPONENT_DEFINE("W4BLiFiOwc");
NS_OBJECT_ENSURE_REGISTERED(LiFiErrorModel);

namespace
{
constexpr double kPi = 3.14159265358979323846;
constexpr double kElectronCharge = 1.602176634e-19;
constexpr double kBoltzmann = 1.380649e-23;

double Clamp(double value, double lower, double upper)
{
    return std::max(lower, std::min(upper, value));
}

double Dot(const Vector& a, const Vector& b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

Vector Normalize(const Vector& value)
{
    const double norm = std::sqrt(Dot(value, value));
    if (norm <= std::numeric_limits<double>::epsilon())
    {
        return Vector(0.0, 0.0, 0.0);
    }
    return Vector(value.x / norm, value.y / norm, value.z / norm);
}

double AngleBetween(const Vector& a, const Vector& b)
{
    return std::acos(Clamp(Dot(Normalize(a), Normalize(b)), -1.0, 1.0));
}

double QFunction(double x)
{
    return 0.5 * std::erfc(x / std::sqrt(2.0));
}
} // namespace

double
LiFiLinkCalculator::LambertianOrder(double halfPowerSemiAngleRad)
{
    NS_ABORT_MSG_IF(!(halfPowerSemiAngleRad > 0.0 && halfPowerSemiAngleRad < kPi / 2.0),
                    "LiFi half-power semi-angle must be in (0, pi/2)");
    return -std::log(2.0) / std::log(std::cos(halfPowerSemiAngleRad));
}

LiFiState
LiFiLinkCalculator::Calculate(const LiFiParameters& parameters,
                               const Vector& txPosition,
                               const Vector& rxPosition,
                               const Vector& txOrientation,
                               const Vector& rxOrientation,
                               double timeS,
                               uint32_t cpeId)
{
    LiFiState state;
    state.timeS = timeS;
    state.cpeId = cpeId;
    const Vector txToRx(rxPosition.x - txPosition.x,
                        rxPosition.y - txPosition.y,
                        rxPosition.z - txPosition.z);
    const Vector rxToTx(-txToRx.x, -txToRx.y, -txToRx.z);
    state.distanceM = std::sqrt(Dot(txToRx, txToRx));
    NS_ABORT_MSG_IF(state.distanceM <= 0.0, "LiFi transmitter and receiver cannot coincide");
    state.irradianceAngleRad = AngleBetween(txOrientation, txToRx);
    state.incidenceAngleRad = AngleBetween(rxOrientation, rxToTx);
    state.lambertianOrder = LambertianOrder(parameters.halfPowerSemiAngleRad);

    state.inFov = state.incidenceAngleRad <= parameters.receiverFovRad &&
                  state.irradianceAngleRad <= kPi / 2.0;
    if (state.inFov)
    {
        const double concentratorGain =
            parameters.concentratorIndex * parameters.concentratorIndex /
            (std::sin(parameters.receiverFovRad) * std::sin(parameters.receiverFovRad));
        state.hLos = ((state.lambertianOrder + 1.0) * parameters.detectorAreaM2 /
                      (2.0 * kPi * state.distanceM * state.distanceM)) *
                     std::pow(std::max(0.0, std::cos(state.irradianceAngleRad)),
                              state.lambertianOrder) *
                     parameters.opticalFilterGain * concentratorGain *
                     std::max(0.0, std::cos(state.incidenceAngleRad));
    }
    else
    {
        state.hLos = 0.0;
    }
    state.receivedPowerW = parameters.txPowerW * state.hLos;
    state.signalCurrentA = parameters.responsivityAperW * state.receivedPowerW;
    state.shotVarianceA2 = 2.0 * kElectronCharge *
                           (state.signalCurrentA + parameters.backgroundCurrentA) *
                           parameters.bandwidthHz;
    state.thermalVarianceA2 = 4.0 * kBoltzmann * parameters.temperatureK *
                              parameters.bandwidthHz / parameters.loadResistanceOhm;
    const double noise = state.shotVarianceA2 + state.thermalVarianceA2;
    state.snr = noise > 0.0 ? state.signalCurrentA * state.signalCurrentA / noise : 0.0;
    state.ber = Clamp(QFunction(std::sqrt(std::max(0.0, state.snr)) / 2.0), 0.0, 0.5);
    const double bits = 8.0 * static_cast<double>(parameters.packetBytes);
    state.per = Clamp(-std::expm1(bits * std::log1p(-state.ber)), 0.0, 1.0);
    return state;
}

LiFiStateLogger::LiFiStateLogger(const std::string& path, double samplePeriodS)
    : m_stream(path, std::ios::out | std::ios::trunc),
      m_samplePeriodS(samplePeriodS)
{
    NS_ABORT_MSG_IF(!m_stream.is_open(), "Cannot open LiFi optical-state CSV: " << path);
    m_stream << "time_s,cpe_id,distance_m,irradiance_angle_rad,incidence_angle_rad,in_fov,"
                "lambertian_order,h_los,received_optical_power_w,signal_current_a,"
                "shot_variance_a2,thermal_variance_a2,snr,ber,per,packet_count,corrupted_packets\n";
}

LiFiStateLogger::~LiFiStateLogger()
{
    if (m_stream.is_open())
    {
        m_stream.flush();
        m_stream.close();
    }
}

void
LiFiStateLogger::Log(const LiFiState& state, uint64_t packetCount, uint64_t corruptedPackets)
{
    auto previous = m_lastSampleS.find(state.cpeId);
    if (previous != m_lastSampleS.end() && state.timeS - previous->second < m_samplePeriodS)
    {
        return;
    }
    m_lastSampleS[state.cpeId] = state.timeS;
    m_stream.setf(std::ios::scientific);
    m_stream << state.timeS << ',' << state.cpeId << ',' << state.distanceM << ','
             << state.irradianceAngleRad << ',' << state.incidenceAngleRad << ','
             << (state.inFov ? 1 : 0) << ',' << state.lambertianOrder << ',' << state.hLos << ','
             << state.receivedPowerW << ',' << state.signalCurrentA << ',' << state.shotVarianceA2
             << ',' << state.thermalVarianceA2 << ',' << state.snr << ',' << state.ber << ','
             << state.per << ',' << packetCount << ',' << corruptedPackets << '\n';
}

TypeId
LiFiErrorModel::GetTypeId()
{
    static TypeId tid =
        TypeId("ns3::W4BLiFiErrorModel")
            .SetParent<ErrorModel>()
            .SetGroupName("Network")
            .AddConstructor<LiFiErrorModel>();
    return tid;
}

LiFiErrorModel::LiFiErrorModel()
    : m_cpeId(0),
      m_uniform(CreateObject<UniformRandomVariable>()),
      m_packetCount(0),
      m_corruptedPackets(0)
{
}

LiFiErrorModel::~LiFiErrorModel() = default;

void
LiFiErrorModel::SetParameters(const LiFiParameters& parameters)
{
    m_parameters = parameters;
}

void
LiFiErrorModel::SetGeometry(Ptr<MobilityModel> transmitter,
                            Ptr<MobilityModel> receiver,
                            const Vector& txOrientation,
                            const Vector& rxOrientation,
                            uint32_t cpeId)
{
    m_transmitter = transmitter;
    m_receiver = receiver;
    m_txOrientation = txOrientation;
    m_rxOrientation = rxOrientation;
    m_cpeId = cpeId;
}

void
LiFiErrorModel::SetLogger(Ptr<LiFiStateLogger> logger)
{
    m_logger = logger;
}

int64_t
LiFiErrorModel::AssignStreams(int64_t stream)
{
    m_uniform->SetStream(stream);
    return 1;
}

const LiFiState&
LiFiErrorModel::GetLastState() const
{
    return m_lastState;
}

bool
LiFiErrorModel::DoCorrupt(Ptr<Packet> packet)
{
    ++m_packetCount;
    m_lastState = LiFiLinkCalculator::Calculate(m_parameters,
                                                 m_transmitter->GetPosition(),
                                                 m_receiver->GetPosition(),
                                                 m_txOrientation,
                                                 m_rxOrientation,
                                                 Simulator::Now().GetSeconds(),
                                                 m_cpeId);
    const bool corrupted = m_uniform->GetValue() < m_lastState.per;
    if (corrupted)
    {
        ++m_corruptedPackets;
    }
    if (m_logger)
    {
        m_logger->Log(m_lastState, m_packetCount, m_corruptedPackets);
    }
    return corrupted;
}

void
LiFiErrorModel::DoReset()
{
    m_packetCount = 0;
    m_corruptedPackets = 0;
}

} // namespace ns3
