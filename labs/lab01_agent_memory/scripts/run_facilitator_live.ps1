[CmdletBinding()]
param(
    [string]$OciConfigFile = "$env:USERPROFILE\.oci\lab01-facilitator-config",
    [string]$OciProfile = "lab01-facilitator",
    [string]$WorkshopCompartmentName = "cmp-khipu-ai-workshop-dev",
    [string]$ChatModelId = "cohere.command-a-03-2025",
    [string]$WalletDirectory = "$env:USERPROFILE\.oci\wallets\khipu-lab01",
    [string]$DatabaseUser = "OAM_T01_P01",
    [string]$DatabaseDsn = "khipuws_low",
    [string]$MemorySchemaOwner = "ADMIN",
    [string]$MemoryStoreId = "KHIPU_LAB01_MEM",
    [string]$TeamCode = "T01",
    [string]$ParticipantCode = "P01"
)

$ErrorActionPreference = "Stop"

function Get-RequiredValue {
    param(
        [string]$Name,
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "Missing required value: $Name"
    }

    return $Value
}

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$python = Join-Path $repositoryRoot ".venv\Scripts\python.exe"
$runner = Join-Path $PSScriptRoot "run_participant_sdk_lab.py"
$bundle = Join-Path $repositoryRoot "labs\lab01_agent_memory\exercises\team_payments_memory.json"
$evidencePath = Join-Path $repositoryRoot "artifacts\lab01\facilitator\oci-sdk-inference-evidence.json"

Get-RequiredValue -Name "OCI config file" -Value $OciConfigFile | Out-Null
Get-RequiredValue -Name "Wallet directory" -Value $WalletDirectory | Out-Null

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Project virtual environment was not found: $python"
}
if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) {
    throw "Participant runner was not found: $runner"
}
if (-not (Test-Path -LiteralPath $bundle -PathType Leaf)) {
    throw "Synthetic team bundle was not found: $bundle"
}
if (-not (Test-Path -LiteralPath $WalletDirectory -PathType Container)) {
    throw "Wallet directory was not found: $WalletDirectory"
}
if (-not (Test-Path -LiteralPath $OciConfigFile -PathType Leaf)) {
    throw "OCI session config was not found: $OciConfigFile"
}

$tenancy = (
    Get-Content -LiteralPath $OciConfigFile |
        Where-Object { $_ -match "^tenancy=" } |
        Select-Object -First 1
) -replace "^tenancy=", ""
Get-RequiredValue -Name "tenancy in OCI session config" -Value $tenancy | Out-Null

$ociArguments = @(
    "--config-file", $OciConfigFile,
    "--profile", $OciProfile,
    "--auth", "security_token"
)
$compartmentResult = & oci iam compartment list `
    --compartment-id $tenancy `
    --compartment-id-in-subtree true `
    --access-level ACCESSIBLE `
    @ociArguments `
    --output json
if ($LASTEXITCODE -ne 0) {
    throw "Unable to list accessible compartments with the facilitator OCI session."
}

$compartment = ($compartmentResult | ConvertFrom-Json).data |
    Where-Object { $_.name -eq $WorkshopCompartmentName -and $_."lifecycle-state" -eq "ACTIVE" } |
    Select-Object -First 1
if ($null -eq $compartment) {
    throw "Workshop compartment '$WorkshopCompartmentName' was not found or is not active."
}

$env:OCI_CONFIG_FILE = $OciConfigFile
$env:OCI_CONFIG_PROFILE = $OciProfile
$env:OCI_COMPARTMENT_ID = $compartment.id
$env:LAB01_CHAT_MODEL_ID = $ChatModelId
$env:LAB01_MAX_OUTPUT_TOKENS = "120"
$env:LAB01_WALLET_DIR = $WalletDirectory
$env:LAB01_DB_USER = $DatabaseUser
$env:LAB01_DB_DSN = $DatabaseDsn
$env:LAB01_MEMORY_SCHEMA_OWNER = $MemorySchemaOwner
$env:LAB01_MEMORY_STORE_ID = $MemoryStoreId

Write-Host "Facilitator preflight passed for compartment '$WorkshopCompartmentName'."
Write-Host "The runner will prompt locally for the application database password and wallet password."
Write-Host "It will make exactly two on-demand OCI Generative AI requests with synthetic workshop data."

& $python $runner `
    --bundle $bundle `
    --team-code $TeamCode `
    --participant-code $ParticipantCode `
    --output-path $evidencePath `
    --confirm-live-inference

exit $LASTEXITCODE
