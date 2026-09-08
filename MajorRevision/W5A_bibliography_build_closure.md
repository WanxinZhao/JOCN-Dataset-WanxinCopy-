# W5A bibliography/build closure

## 1. Verdict

**`PASS_BIBLIOGRAPHY_BUILD_CLOSED`**

The active bibliography is `sample.bib`, loaded only by
`JOCN_Telemetry.tex:579` through `\bibliography{sample.bib}`. The
build-blocking duplicate-key, unescaped-ampersand, and stray code-fence
defects were fixed with the smallest source-level changes needed. No
manuscript scientific text, wireless result, figure data, table value, claim
boundary, or reviewer-response substance was changed in W5A.

## 2. Original blockers before editing

### Active bibliography path

Only one `.bib` source is active for this manuscript:

```text
JOCN_Telemetry.tex:579 -> sample.bib
```

No `\addbibresource` or second bibliography source was found in the active
manuscript. The repository working tree contained only `sample.bib` as a BibTeX
database in the build tree.

### Duplicate citation keys

The pre-edit `sample.bib` contained 120 entry records, 88 unique keys, 23
duplicate-key groups, and 32 extra duplicate occurrences. The prior BibTeX
attempt reported 26 repeated-entry diagnostics before stopping. The complete
pre-edit duplicate inventory, with original entry-start line numbers, was:

| Key | Original entry lines |
|---|---:|
| `rfc9232` | 14, 584, 955 |
| `gnmi2018` | 24, 594, 1005 |
| `shen2025telemetry` | 65, 574 |
| `xie2022task` | 88, 606, 1013 |
| `ma2023explainable` | 99, 616, 1023 |
| `alemi2017vib` | 110, 624, 1031 |
| `edwards2016censor` | 117, 631, 1038 |
| `madras2018fair` | 124, 638, 1045 |
| `zhai2024alibaba` | 278, 539, 924 |
| `he2023qot` | 289, 560, 945 |
| `pan2010opm` | 479, 813 |
| `dong2016opm` | 489, 823 |
| `tanimura2019cnn` | 499, 833 |
| `xiang2021osnr` | 509, 843 |
| `saif2021opm` | 519, 853 |
| `filer2016microsoft` | 529, 914 |
| `delezoide2020field` | 550, 935 |
| `zhuge2023dt` | 650, 1053 |
| `curri2022gnpy` | 660, 1063 |
| `riley2010ns3` | 693, 1073 |
| `he2023isac` | 771, 863 |
| `zhao2025vibration` | 782, 874 |
| `sun2019application` | 791, 892 |

All duplicate groups represented the same publication under the same key;
none required a citation-key rename. Several later records were abbreviated
or differed in optional metadata. The earliest occurrence was retained as the
canonical existing entry. This preserves the existing key and avoids
inventing or reconciling bibliographic metadata. In particular, the first
`he2023qot` record was retained because it was the more complete existing
record (including DOI and issue metadata).

### Unescaped ampersands

The pre-edit literal ampersands were:

| Original line | Entry key | Field |
|---:|---|---|
| 168 | `8792139` | `journal={IEEE Communications Surveys & Tutorials}` |
| 421 | `Chen2019IEEE` | `journal={IEEE Communications Surveys & Tutorials}` |
| 1134 | `sun2019IEEE` | `journal={IEEE Communications Surveys & Tutorials}` |

Each was changed locally to `\&`. Already escaped ampersands in other fields
were left unchanged.

### Other source-syntax defect

Two Markdown code-fence lines had been embedded in `sample.bib`:

- original line 812: ```` ```bibtex ````;
- original line 1115: ```` ``` ````.

They were removed. No citation or bibliographic field was contained in those
two fence lines.

## 3. Files changed

| File | W5A change |
|---|---|
| `sample.bib` | Removed only later duplicate entries, escaped the three literal ampersands, and removed the two stray Markdown fence lines. |
| `MajorRevision/W5A_bibliography_build_closure.md` | This closure report. |

`JOCN_Telemetry.tex` was not edited in W5A. Its existing W4D wireless changes
remain in the working tree but were not touched. The generated `.aux`, `.bbl`,
`.log`, and PDF are build artifacts, not scientific source changes.

## 4. Post-fix syntax state

After the local fixes, `sample.bib` contains 88 parsed entries and 88 unique
keys. A read-only source scan found:

- zero duplicate citation keys;
- zero unescaped literal ampersands;
- zero remaining Markdown code fences;
- no detected unmatched-brace or malformed-entry condition.

No citation keys were renamed, and no manuscript citation commands were
changed.

## 5. Strict build result

The normal build command was run from `/tmp/jocn-w0-github`:

```text
latexmk -pdf -interaction=nonstopmode -file-line-error JOCN_Telemetry.tex
```

Result:

- exit code: `0`;
- BibTeX: completed with no errors;
- LaTeX: completed with no fatal error;
- PDF: generated as `JOCN_Telemetry.pdf`, 14 pages;
- undefined citations: `0` detected;
- undefined references: `0` detected;
- fatal bibliography/syntax diagnostics: `0` detected.

## 6. Remaining non-fatal warnings

The successful build still reports warnings that were not necessary to change
for W5A:

- BibTeX empty-author warnings for `3gpp28552` and `etsi128554`;
- the existing package-name warning for `legacy-styles/jocn` versus the
  package-provided name;
- an existing missing `TS1/phv/b/sc` font shape warning;
- existing underfull hbox/vbox warnings, including table and paragraph
  layout warnings;
- a pdfTeX page-group warning when the two existing W4C PDF figures are
  included on one page.

No `Overfull \\hbox` warning was found in the final log. The remaining items
are non-fatal and are outside the requested narrow bibliography closure.

## 7. Visual build check

Pages 11--14 were rendered with `pdftoppm` and visually inspected. The result
shows:

- Table 4 present and readable;
- Figure 8 present with final W4C terminology;
- Figure 9 present with final LiFi/OWC FOV terminology;
- references section present;
- citations rendered as numbered references, including the two LiFi equation
  references;
- no missing-image placeholder;
- no visibly broken bibliography layout;
- no bibliography-fix-induced clipping or overlap.

## 8. Scientific non-change confirmation

W5A changed bibliography/build syntax only. Specifically:

- no wireless simulation was run;
- no W4C data, result, figure source, or table value was changed;
- no optical or semantic experiment was changed;
- no scientific claim or limitation was rewritten;
- no reviewer-response substance was changed;
- no citation key was updated;
- no commit or push was performed.

W5A_VERDICT=PASS_BIBLIOGRAPHY_BUILD_CLOSED
ACTIVE_BIBLIOGRAPHY=sample.bib_ONLY_VIA_JOCN_Telemetry.tex_579
DUPLICATE_KEYS_FIXED=23_GROUPS_32_EXTRA_OCCURRENCES_REMOVED_CANONICAL_FIRST_ENTRIES_RETAINED
UNESCAPED_AMPERSANDS_FIXED=3_ENTRIES_8792139_CHEN2019IEEE_SUN2019IEEE
OTHER_BIB_SYNTAX_FIXES=2_STRAY_MARKDOWN_CODE_FENCES_REMOVED
CITATION_KEYS_UPDATED=NO
UNDEFINED_CITATIONS=0
UNDEFINED_REFERENCES=0
PDF_BUILD_STATUS=PASS_LATEXMK_EXIT_0_14_PAGE_PDF_GENERATED
WIRELESS_CONTENT_CHANGED=NO
SCIENTIFIC_CONTENT_CHANGED=NO
READY_FOR_W5B_MANUSCRIPT_CLOSEOUT=YES
