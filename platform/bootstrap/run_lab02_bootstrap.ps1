[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^p(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})$')]
    [string]$ParticipantId,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$WalletPath,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9_]+$')]
    [string]$ConnectAlias,

    [Parameter(Mandatory = $true)]
    [ValidateSet('schema', 'table', 'audit')]
    [string]$Mode,

    [int]$VectorDimension = 1536
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$python = Join-Path $repositoryRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw 'Project virtual environment is unavailable.'
}
if (-not (Test-Path -LiteralPath $WalletPath -PathType Container)) {
    throw 'Wallet directory is unavailable.'
}

$env:LAB02_BOOTSTRAP_USERNAME = 'ADMIN'
$env:ADB_CONNECT_STRING = $ConnectAlias
$env:ADB_WALLET_DIR = $WalletPath

if ($Mode -eq 'schema') {
    & $python (Join-Path $PSScriptRoot 'create_lab02_participant.py') `
        '--participant-id' $ParticipantId '--confirm-create-participant'
} elseif ($Mode -eq 'table') {
    $env:ADB_USERNAME = "KHIPU_L2_$($ParticipantId.ToUpper())"
    & $python (Join-Path $PSScriptRoot 'create_lab02_participant_table.py') `
        '--participant-id' $ParticipantId '--vector-dimension' $VectorDimension `
        '--confirm-create-table'
} else {
    & $python (Join-Path $PSScriptRoot 'audit_lab02_participant.py') `
        '--participant-id' $ParticipantId
}

if ($LASTEXITCODE -ne 0) {
    throw "Lab 2 $Mode bootstrap failed; audit privately before retrying."
}
