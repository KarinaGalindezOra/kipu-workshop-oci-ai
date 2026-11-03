[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$SessionPath,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Question,

    [ValidateSet('v1', 'v2')]
    [string]$ContractVersion
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
$arguments = @(
    (Join-Path $repositoryRoot 'labs\lab02_contract_rag\scripts\run_live_validation.py'),
    '--question', $Question,
    '--confirm-live-inference',
    '--output-dir', $env:LAB02_REPORT_ROOT
)
if ($ContractVersion) {
    $arguments += @('--contract-version', $ContractVersion)
}
& $python $arguments
if ($LASTEXITCODE -ne 0) {
    throw 'Participant live RAG query failed; inspect the private evidence report.'
}
