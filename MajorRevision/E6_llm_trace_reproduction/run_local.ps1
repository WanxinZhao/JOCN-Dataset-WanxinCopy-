param(
    [string]$CodeRoot = 'F:\BaiduSyncdisk\6-Pythonproject\ECOC2026_Code\oopt-gnpy',
    [string]$PythonExe = 'F:\BaiduSyncdisk\1-论文\7-Datageneration\JOCN-Dataset\.runtime\llm-trace-reproduction\Scripts\python.exe'
)

$ErrorActionPreference = 'Stop'
$experimentDir = $PSScriptRoot
$e5Source = Join-Path (Split-Path $experimentDir -Parent) 'E5_recovered_gnpy_replay\source'
$envFile = Join-Path $CodeRoot '.env'
$keyConfigured = [bool]$env:OPENAI_API_KEY

if (-not $keyConfigured -and (Test-Path -LiteralPath $envFile)) {
    $keyLine = Get-Content -LiteralPath $envFile | Where-Object {
        $_ -match '^\s*OPENAI_API_KEY\s*=\s*.+$'
    } | Select-Object -First 1
    $keyConfigured = [bool]$keyLine
}

if (-not $keyConfigured) {
    throw 'OPENAI_API_KEY is not configured. Put it in oopt-gnpy/.env (which is Git-ignored) and rerun this script.'
}
if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python environment not found: $PythonExe"
}
if (-not (Test-Path -LiteralPath $CodeRoot)) {
    throw "Code repository not found: $CodeRoot"
}

$env:LLM_PROVIDER = 'openai'
$env:LLM_STRICT_MODE = '1'
$env:LLM_MAX_RETRIES = '3'
$env:LLM_TIMEOUT_SECONDS = '90'
$env:OPENAI_MODEL = 'gpt-4o-mini-2024-07-18'
$env:PHYSICAL_LAYER_DB_BACKEND = 'file'
$env:TOPOLOGY_PATH = Join-Path $e5Source 'NDFF_Testbed.json'
$env:EQUIPMENT_PATH = Join-Path $e5Source 'eqpt_config_NDFF_schema_fixed.json'
$env:RUN_BASE_DIR = Join-Path $experimentDir 'runs'
$env:OPENAI_PRICING_SNAPSHOT_DATE = '2026-09-12'
$env:OPENAI_INPUT_USD_PER_1M_TOKENS = '0.15'
$env:OPENAI_CACHED_INPUT_USD_PER_1M_TOKENS = '0.075'
$env:OPENAI_OUTPUT_USD_PER_1M_TOKENS = '0.60'
$env:OPENAI_PRICING_SOURCE = 'https://developers.openai.com/api/docs/models/gpt-4o-mini'

$request = 'Generate a raw QoT dataset for all NDFF paths starting from Bristol using 8 Voyager transmitters only. Use 8 channel slots and enumerate all binary on/off channel patterns across the 8 slots. Simulate only QPSK and 16QAM.'

Push-Location -LiteralPath $CodeRoot
try {
    & $PythonExe main.py --request $request --max-iterations 2
    if ($LASTEXITCODE -ne 0) {
        throw "Reproduction failed with exit code $LASTEXITCODE. Inspect the newest runs/<run_id>/llm_trace directory."
    }
}
finally {
    Pop-Location
}
