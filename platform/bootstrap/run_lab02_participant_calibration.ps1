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
& $python (Join-Path $repositoryRoot 'labs\lab02_contract_rag\scripts\calibrate_participant.py') `
    '--confirm-live-inference'
if ($LASTEXITCODE -ne 0) {
    throw 'Calibration failed; inspect private configuration before retrying.'
}
