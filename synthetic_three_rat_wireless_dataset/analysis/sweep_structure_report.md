# Synthetic three-RAT dataset structure check

Run configurations: **48/48**. Application rows: **432/432**. Raw FlowMonitor rows: **624** ([13] per run).

Branch rows: NR=144, WiFi80211ax=144, LiFi=144. Duplicate application keys: 0. Missing configuration keys: 0; extra configuration keys: 0; duplicate configuration keys: 0. All per-run structure checks: **PASS**. All required KPI values finite: **PASS**. All tuple/interface mappings: **PASS**.

The application table contains one row per run × branch × CPE. Raw FlowMonitor XML rows include non-application EPC/control flows and are not mixed into the application table.
