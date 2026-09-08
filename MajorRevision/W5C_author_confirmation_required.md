# W5C author confirmation required

This is the minimum factual confirmation list remaining after the W5C-A
artifact audit. Items are listed only where the current files cannot establish
the answer. No answer should be inferred from a filename, timestamp, or
Croissant metadata assertion.

## Required for final manuscript/response closure

1. **Voyager optical product lineage**
   - Is `semantic_case_v6/data/voyager.csv` the intended primary file for the
     339-km optical dataset and the E1/E2 benchmark?
   - What is the actual physical campaign period for that product?
   - Do the 2023-12-26--2024-01-26 and 10-s/raw-to-15-min statements refer to
     a different raw or processed product? If yes, provide its exact file
     path/release and explain the transformation to `voyager.csv`.
   - Were the current 2025-12-22--2026-01-24 timestamp values shifted,
     anonymised, regenerated, or otherwise transformed? If unknown, state
     that explicitly.

2. **External optical datasets**
   - For the 986-km NDFF QoT data, provide the authoritative release/source
     path, record counts, timestamp coverage, file formats/sizes, and the
     applicable terms.
   - For the deployed urban fibre-sensing data, provide the authoritative
     MAT/CSV release path, record counts, timestamp coverage, file sizes, and
     applicable terms.

3. **Wireless field definitions**
   - Confirm the physical units and exact definitions of the traffic, signal,
     and inactivity columns used by `run_e1_e2.py`.

4. **Release terms and paths**
   - Confirm the formal licence or repository terms for every claimed raw,
     derived, and synthetic artifact, including the final W4C bundle.
   - Confirm whether the constructed fusion benchmark is released as a
     materialized file or is intentionally code-reconstructable only.

5. **Reviewer-letter identifiers**
   - Verify the original reviewer comment text and numbering. In particular,
     local materials assign R3C4 inconsistently to the GNPy and wireless
     correctness concerns; the final response must use the original letter's
     identifier.

## Conditional confirmations

6. **LLM provenance**
   - If original records exist, provide model/provider/version, prompts/tool
     schema, calls, retries, token/cost/latency data, and human interventions.
   - If they do not exist, confirm that these quantities are unavailable and
     will remain explicitly unreported; no LLM-superiority claim is then made.

7. **GNPy numerical replay**
   - If independent numerical reproduction is required by the original
     comment, provide the original working GNPy commit/container and the
     corresponding equipment/configuration files. Otherwise confirm that the
     paper should retain only the bounded artifact-audit claim.

## Not requested from the authors

- No new simulation or ML experiment is required for the current bounded
  claims.
- No new wireless/ns-3 validation is required; W4C/W4E remains frozen.
- No timestamp-level optical-wireless pairing should be fabricated.
