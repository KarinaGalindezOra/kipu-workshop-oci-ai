[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$TeamCode,
    [Parameter(Mandatory)]
    [string]$ParticipantCode,
    [string]$SessionFile,
    [switch]$Preflight,
    [ValidateSet("payment-idempotency", "contract-compatibility")]
    [string]$MemoryExercise,
    [switch]$ContextExperiment
)

$ErrorActionPreference = "Stop"

function Require-EnvironmentValue {
    param([string]$Name)

    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Missing required environment variable: $Name"
    }
    return $value
}

if ($SessionFile) {
    $resolvedSessionFile = Resolve-Path -LiteralPath $SessionFile -ErrorAction Stop
    . $resolvedSessionFile
}

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$python = Join-Path $repositoryRoot ".venv\Scripts\python.exe"
$runner = Join-Path $PSScriptRoot "run_participant_sdk_lab.py"
$bundle = Join-Path $repositoryRoot "labs\lab01_agent_memory\exercises\team_payments_memory.json"

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Project virtual environment was not found: $python"
}
if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) {
    throw "Participant runner was not found: $runner"
}
if (-not (Test-Path -LiteralPath $bundle -PathType Leaf)) {
    throw "Synthetic team bundle was not found: $bundle"
}

$walletDirectory = Require-EnvironmentValue "LAB01_WALLET_DIR"
$null = Require-EnvironmentValue "LAB01_DB_USER"
$null = Require-EnvironmentValue "LAB01_DB_DSN"
$null = Require-EnvironmentValue "LAB01_MEMORY_SCHEMA_OWNER"
$null = Require-EnvironmentValue "LAB01_MEMORY_STORE_ID"

if (-not (Test-Path -LiteralPath $walletDirectory -PathType Container)) {
    throw "Wallet directory was not found: $walletDirectory"
}

Write-Host "LAB01_LAUNCHER_READY"
Write-Host "LAB01_WALLET_READY True"
Write-Host "LAB01_MEMORY_CONFIGURATION_READY True"

$runnerArguments = @(
    $runner,
    "--bundle", $bundle,
    "--team-code", $TeamCode,
    "--participant-code", $ParticipantCode
)

if (($Preflight -and $MemoryExercise) -or ($Preflight -and $ContextExperiment) -or ($MemoryExercise -and $ContextExperiment)) {
    throw "Choose exactly one of -Preflight, -MemoryExercise, or -ContextExperiment."
}

if ($Preflight) {
    Write-Host "LAB01_PREFLIGHT_NO_INFERENCE"
    & $python @runnerArguments --preflight
    exit $LASTEXITCODE
}

if ($MemoryExercise) {
    $safeTeamCode = $TeamCode.Trim().ToLowerInvariant()
    $safeParticipantCode = $ParticipantCode.Trim().ToLowerInvariant()
    $evidencePath = Join-Path $repositoryRoot "artifacts\lab01\$safeTeamCode\$safeParticipantCode\memory-exercise-$MemoryExercise-evidence.json"

    Write-Host "LAB01_MEMORY_EXERCISE_AUTHORIZED"
    Write-Host "This run persists and retrieves synthetic ADB memory only. It makes zero OCI Generative AI requests."
    & $python @runnerArguments `
        "--memory-exercise" $MemoryExercise `
        "--output-path" $evidencePath
    exit $LASTEXITCODE
}

if ($ContextExperiment) {
    $safeTeamCode = $TeamCode.Trim().ToLowerInvariant()
    $safeParticipantCode = $ParticipantCode.Trim().ToLowerInvariant()
    $experiment = Join-Path $repositoryRoot "labs\lab01_agent_memory\exercises\context-economy-experiment.json"
    $evidencePath = Join-Path $repositoryRoot "artifacts\lab01\$safeTeamCode\$safeParticipantCode\context-economy-experiment-evidence.json"

    if (-not (Test-Path -LiteralPath $experiment -PathType Leaf)) {
        throw "Context experiment file was not found: $experiment"
    }
    $ociConfigFile = Require-EnvironmentValue "OCI_CONFIG_FILE"
    $null = Require-EnvironmentValue "OCI_CONFIG_PROFILE"
    $null = Require-EnvironmentValue "OCI_COMPARTMENT_ID"
    $null = Require-EnvironmentValue "LAB01_CHAT_MODEL_ID"
    if (-not (Test-Path -LiteralPath $ociConfigFile -PathType Leaf)) {
        throw "OCI configuration file was not found: $ociConfigFile"
    }

    Write-Host "LAB01_CONTEXT_EXPERIMENT_READY"
    Write-Host "This run makes four on-demand OCI Generative AI calls with approved synthetic contexts."
    & $python @runnerArguments `
        "--context-experiment" $experiment `
        "--output-path" $evidencePath `
        "--confirm-context-experiment"
    exit $LASTEXITCODE
}

$ociConfigFile = Require-EnvironmentValue "OCI_CONFIG_FILE"
$ociProfile = Require-EnvironmentValue "OCI_CONFIG_PROFILE"
$null = Require-EnvironmentValue "OCI_COMPARTMENT_ID"
$null = Require-EnvironmentValue "LAB01_CHAT_MODEL_ID"

if (-not (Test-Path -LiteralPath $ociConfigFile -PathType Leaf)) {
    throw "OCI configuration file was not found: $ociConfigFile"
}

Write-Host "LAB01_OCI_PROFILE_READY True"
Write-Host "OCI authentication will be verified by the first on-demand inference request."

$safeTeamCode = $TeamCode.Trim().ToLowerInvariant()
$safeParticipantCode = $ParticipantCode.Trim().ToLowerInvariant()
$evidencePath = Join-Path $repositoryRoot "artifacts\lab01\$safeTeamCode\$safeParticipantCode\oci-inference-evidence.json"

Write-Host "LAB01_LIVE_RUN_AUTHORIZED"
Write-Host "This run makes exactly two on-demand OCI Generative AI requests with synthetic data."
& $python @runnerArguments `
    "--output-path" $evidencePath `
    "--confirm-live-inference"

exit $LASTEXITCODE
