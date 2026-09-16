# ns-3 claim and terminology boundary

This lock is based on the archived source and the W1 validation evidence. It is intended to prevent the synthetic wireless results from being described as physical measurements or as technology-universal laws.

## Terminology that is supported

| Supported label | Evidence | Claim form |
| --- | --- | --- |
| LTE/EPC | Stock ns-3 LTE helper plus PointToPointEpcHelper; archived source `generated.cc:L141-L152`. | Use `LTE/EPC`; do not call this 5G NR. |
| Wi-Fi 802.11n | `wifi.SetStandard(WIFI_STANDARD_80211n)` with Yans channel/PHY; `generated.cc:L112-L124`. | Use Wi-Fi 802.11n for this synthetic branch. A separate physical testbed can be described independently. |
| CSMA-based LiFi surrogate | `CsmaHelper`, 50/100 Mbps and 10 ns delay; `generated.cc:L130-L139`. | Call it an idealized CSMA-based LiFi surrogate. |
| Finite configuration-specific comparison | 48 archived configurations, grouped in `grouped_kpi_summary.csv`. | Report observed deltas for this sweep only. |

## Claims that are not supported

| Overclaim | Reason | Boundary |
| --- | --- | --- |
| 5G NR performance | The implementation is LTE/EPC; `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/schema.py:L125-L129` explicitly rejects 5G NR in this install. | Unsupported. |
| Physical LiFi propagation | No optical LOS/FOV geometry, photodiode, optical modulation, shot noise, blockage, or calibrated optical error model is present in the CSMA branch. | Unsupported. |
| Universal ranking such as LiFi always has lower delay/jitter | The lower jitter occurs under the idealized CSMA/10 ns configuration and changes at high load. | Unsupported; phrase as an observed configuration-specific result. |
| Measured wireless testbed validation | This artifact is synthetic ns-3 output; no measured wireless ground truth is part of this validation. | Unsupported. |
| Zero terminal packet loss | FlowMonitor `lostPackets` is not equal to `txPackets-rxPackets` at the exact 10 s stop. | Unsupported unless a separate terminal-loss definition is reported. |

Recommended sentence: `Under the adopted idealized CSMA-based LiFi-surrogate configuration, the surrogate branch exhibits the observed delay/jitter behaviour relative to the LTE/EPC and Wi-Fi branches; this is not a physical LiFi propagation result.`

Evidence: `/home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/kpi_recomputation_summary.json`, `grouped_kpi_summary.csv`, `replay_results.csv`, and this file.
