# Independent hand-written ns-3 reference report

The reference is a new fixed-configuration C++ program at /home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/independent_reference/reference.cc. It was compiled with the existing ns-3.44 build libraries and run at the medium archived operating point:

- duration: 10 s
- seed: 2
- offered load: 10 Mbps per application flow
- packet size: 1024 bytes
- mobility speed: 3 m/s
- CSMA LiFi-surrogate rate: 100 Mbps
- three CPEs and three access branches, with nine downlink UDP flows

## Structural comparison

- generated application flows: 9
- reference application flows: 9
- all expected flows present: True
- flow comparison key: XML classifier-derived access type and CPE, not the numeric FlowMonitor ID

## Numerical comparison

The per-flow tolerance is exact equality for packet counters, 1e-12 for the FlowMonitor loss ratio, and max(1e-6, 1%) for continuous KPIs. The tolerance is a comparison rule, not a claim of physical uncertainty.

- status counts: {'CONSISTENT': 63}
- topology/configuration checks: {'checks': 5, 'consistent': 5, 'materially_different': 0}
- tx_packets: {'records': 9, 'consistent': 9, 'materially_different': 0, 'max_absolute_delta': 0.0}
- rx_packets: {'records': 9, 'consistent': 9, 'materially_different': 0, 'max_absolute_delta': 0.0}
- flowmonitor_lost_packets: {'records': 9, 'consistent': 9, 'materially_different': 0, 'max_absolute_delta': 0.0}
- packet_loss_ratio: {'records': 9, 'consistent': 9, 'materially_different': 0, 'max_absolute_delta': 0.0}
- throughput_mbps: {'records': 9, 'consistent': 9, 'materially_different': 0, 'max_absolute_delta': 0.0}
- mean_delay_ms: {'records': 9, 'consistent': 9, 'materially_different': 0, 'max_absolute_delta': 0.0}
- mean_jitter_ms: {'records': 9, 'consistent': 9, 'materially_different': 0, 'max_absolute_delta': 0.0}

## Interpretation

The hand-written reference independently instantiates the same declared topology, access mapping, application count, and stock ns-3.44 modelling assumptions. A CONSISTENT result means the per-flow value met the stated comparison tolerance. This does not turn the CSMA LiFi surrogate into a physical optical model and does not validate universal cross-technology rankings.

Evidence files:

- source: /home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/independent_reference/reference.cc
- generated comparison input: /home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/replays/medium_load_high_mobility/fresh_results/flowmon.xml
- reference FlowMonitor XML: /home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/independent_reference/results/flowmon.xml
- keyed comparison: /home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/independent_reference/comparison.csv
- topology/configuration comparison: /home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/independent_reference/topology_config_comparison.csv
- execution logs: /home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/independent_reference/compile.log, /home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/independent_reference/run.log
