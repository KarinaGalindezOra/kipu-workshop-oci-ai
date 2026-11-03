[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$SessionPath
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$python = Join-Path $repositoryRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw 'Project virtual environment is unavailable.'
}
if (-not (Test-Path -LiteralPath $SessionPath -PathType Leaf)) {
    throw 'Private participant session file is unavailable.'
}

. $SessionPath
$measurements = 'C:\KhipuPrivate\lab02-development-measurements.json'
if (Test-Path -LiteralPath $env:LAB02_CALIBRATION_FILE -PathType Leaf) {
    throw 'Frozen calibration already exists; do not overwrite it.'
}
if (-not (Test-Path -LiteralPath $measurements -PathType Leaf)) {
    & $python (Join-Path $repositoryRoot 'labs\lab02_contract_rag\scripts\collect_calibration.py') `
        '--confirm-live-inference' '--output' $measurements
    if ($LASTEXITCODE -ne 0) {
        throw 'Development measurement collection failed; audit privately before retrying.'
    }
} else {
    Write-Host 'Reusing existing private development measurements; no new embedding calls are made.'
}
& $python (Join-Path $repositoryRoot 'labs\lab02_contract_rag\scripts\calibrate.py') `
    '--measurements' $measurements '--output' $env:LAB02_CALIBRATION_FILE
if ($LASTEXITCODE -ne 0) {
    throw 'Calibration freeze failed; inspect private development measurements.'
}
