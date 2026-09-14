# Response letter

`response_letter.tex` is the submission-facing point-by-point response for the
current manuscript revision. It contains the detailed architecture rationale,
LLM trace and recovery chronology, provenance handling, warning counts, and
other reviewer-requested evidence that was intentionally removed from the main
article for readability.

Compile from this directory with:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error response_letter.tex
```

The main manuscript remains `../../JOCN_Telemetry.tex`.
