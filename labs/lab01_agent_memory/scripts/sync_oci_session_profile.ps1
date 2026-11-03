[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$SourceConfigFile,
    [Parameter(Mandatory)]
    [string]$ProfileName,
    [string]$TargetConfigFile = (Join-Path $env:USERPROFILE ".oci\config")
)

$ErrorActionPreference = "Stop"

function Get-ProfileBlock {
    param(
        [Parameter(Mandatory)][string]$ConfigText,
        [Parameter(Mandatory)][string]$Profile
    )

    $escapedProfile = [regex]::Escape($Profile)
    $pattern = "(?ms)^\[$escapedProfile\]\r?\n.*?(?=^\[|\z)"
    return [regex]::Match($ConfigText, $pattern)
}

$resolvedSource = (Resolve-Path -LiteralPath $SourceConfigFile -ErrorAction Stop).Path
$sourceText = [System.IO.File]::ReadAllText($resolvedSource)
$sourceProfile = Get-ProfileBlock -ConfigText $sourceText -Profile $ProfileName
if (-not $sourceProfile.Success) {
    throw "OCI profile '$ProfileName' was not found in the private source config file."
}

$targetDirectory = Split-Path -Parent $TargetConfigFile
New-Item -ItemType Directory -Force -Path $targetDirectory | Out-Null

$backupCreated = $false
if (Test-Path -LiteralPath $TargetConfigFile -PathType Leaf) {
    $targetText = [System.IO.File]::ReadAllText($TargetConfigFile)
    $backupPath = "$TargetConfigFile.workshop-backup"
    Copy-Item -LiteralPath $TargetConfigFile -Destination $backupPath -Force
    $backupCreated = $true
} else {
    $targetText = ""
}

$targetProfile = Get-ProfileBlock -ConfigText $targetText -Profile $ProfileName
if ($targetProfile.Success) {
    $updatedText = $targetText.Substring(0, $targetProfile.Index) + $sourceProfile.Value + `
        $targetText.Substring($targetProfile.Index + $targetProfile.Length)
} elseif ([string]::IsNullOrWhiteSpace($targetText)) {
    $updatedText = $sourceProfile.Value
} else {
    $updatedText = $targetText.TrimEnd("`r", "`n") + "`r`n`r`n" + $sourceProfile.Value
}

[System.IO.File]::WriteAllText($TargetConfigFile, $updatedText, [System.Text.UTF8Encoding]::new($false))

Write-Host "OCI_STANDARD_PROFILE_READY True"
Write-Host "The named session profile was synchronized locally without printing token, OCID, or user values."
Write-Host "OCI_STANDARD_CONFIG_BACKUP_CREATED $backupCreated"
