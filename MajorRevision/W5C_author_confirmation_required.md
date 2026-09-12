# Remaining author confirmations after provenance closure

The Voyager campaign identity, reviewer numbering, final W4C release, and
GNPy numerical replay are now resolved. This file lists only facts that the
available primary artifacts still cannot establish.

## Confirmed and closed

- `semantic_case_v6/data/voyager.csv` is the optical source used by E1/E2.
  It is a separate Christmas 2025 campaign on the same 339-km NDFF loop as
  the earlier public dataset. Its real timestamps span 2025-12-22 16:38:43
  to 2026-01-24 16:10:55; they were not shifted or anonymised.
- The 2023-12-26--2024-01-26, 10-s-to-15-min description belongs to the
  earlier 1,373-record, four-channel processed product, not to the 20,960-row
  E1/E2 source.
- The byte-identical 20,960-row source is public under
  `OTN Monitoring Data_one_month/NDFF_Voyager_Christmas_2025/`, SHA-256
  `879d7b6143b04b995165360d1600b81b8134312fed08b2bdeb577b5cb8b6e209`.
- The exact leakage-controlled constructed benchmark is now released as a
  2,848-row, 52-field table at
  `semantic_case_v6/data/cross_domain_fusion_dataset.csv`, SHA-256
  `6f290cddd06836042699a6cff615aff90fb3e30a2d3790e1cdf92d8c01412681`.
- The final W4C source, data dictionary, run outputs, and aggregate tables are
  public under `W4C_THREE_RAT_SWEEP/` in the revision repository.
- Reviewer 3 Comment 4 is the independent-correctness/reproducibility comment.
- E5 now supplies a 96-case GNPy numerical replay in both the pinned v2.12
  compatibility environment and the schema-corrected v2.14.2 environment.

## Still requiring author confirmation

1. **External optical datasets**
   - For the 986-km NDFF QoT data, confirm the authoritative release path,
     exact record counts, timestamp coverage, file sizes, and reuse terms.
   - For the deployed urban fibre-sensing data, confirm the authoritative
     MAT/CSV release path, exact record counts, timestamp coverage, aggregate
     size, and reuse terms.

2. **Practical wireless field definitions**
   - Confirm the physical units and authoritative definitions of the traffic,
     signal, temperature, power, bitrate, and inactivity columns. The current
     field dictionary marks undocumented units explicitly.

3. **Formal release terms**
   - Decide whether to add a standard top-level licence/SPDX identifier. The
     practical repository currently states academic, non-commercial terms in
     its README; the revision/W4C repository does not state formal terms.

4. **Historical LLM run provenance**
   - The provider is now author-confirmed as OpenAI, and the complete source
     prompt templates are released.
   - If original run records exist, supply the date-stamped model snapshot,
     rendered calls/responses, retries, tokens, cost, latency, failures, and
     human interventions.
   - If they do not exist, retain the manuscript's explicit `not reported`
     statement and the bounded workflow-feasibility claim.

## No further experiment required for current bounded claims

- E1/E2 need not be rerun because the newly published Voyager file matches the
  experiment-source SHA-256 exactly.
- No additional GNPy or wireless simulation is required for the current
  correctness and feasibility wording.
- No timestamp-level optical--wireless pairing should be inferred or created.
