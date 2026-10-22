[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ConfigFile,
    [Parameter(Mandatory)]
    [string]$ProfileName
)

$ErrorActionPreference = "Stop"

function ConvertFrom-Base64Url {
    param([Parameter(Mandatory)][string]$Value)

    $base64 = $Value.Replace("-", "+").Replace("_", "/")
    $padding = (4 - ($base64.Length % 4)) % 4
    $base64 += "=" * $padding
    return [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($base64))
}

$resolvedConfig = (Resolve-Path -LiteralPath $ConfigFile -ErrorAction Stop).Path
$configText = [System.IO.File]::ReadAllText($resolvedConfig)
$escapedProfile = [regex]::Escape($ProfileName)
$profilePattern = "(?ms)(?<header>^\[$escapedProfile\]\r?\n)(?<body>.*?)(?=^\[|\z)"
$profileMatch = [regex]::Match($configText, $profilePattern)
if (-not $profileMatch.Success) {
    throw "OCI profile '$ProfileName' was not found in the private config file."
}

$body = $profileMatch.Groups["body"].Value
$tokenMatch = [regex]::Match($body, "(?m)^security_token_file\s*=\s*(?<path>.+?)\s*$")
if (-not $tokenMatch.Success) {
    throw "OCI profile '$ProfileName' is missing security_token_file."
}

$tokenPath = $tokenMatch.Groups["path"].Value.Trim()
if (-not [System.IO.Path]::IsPathRooted($tokenPath)) {
    $tokenPath = Join-Path (Split-Path -Parent $resolvedConfig) $tokenPath
}
if (-not (Test-Path -LiteralPath $tokenPath -PathType Leaf)) {
    throw "The configured security token file was not found. Authenticate a new OCI session instead."
}

$jwtParts = ([System.IO.File]::ReadAllText($tokenPath)).Trim().Split(".")
if ($jwtParts.Count -ne 3) {
    throw "The configured security token is not a valid JWT. Authenticate a new OCI session instead."
}
$payload = ConvertFrom-Json (ConvertFrom-Base64Url $jwtParts[1])
$userId = [string]$payload.sub
if (-not $userId.StartsWith("ocid1.user.")) {
    throw "The security token does not contain a valid OCI user subject."
}

$userPattern = "(?m)^user\s*=\s*.*(?:\r?\n|$)"
if ([regex]::IsMatch($body, $userPattern)) {
    $updatedBody = [regex]::Replace($body, $userPattern, "user=$userId`r`n", 1)
} else {
    $lineEnding = if ($body.Contains("`r`n")) { "`r`n" } else { "`n" }
    $updatedBody = $body.TrimEnd("`r", "`n") + $lineEnding + "user=$userId" + $lineEnding
}

$updatedProfile = $profileMatch.Groups["header"].Value + $updatedBody
$updatedConfig = $configText.Substring(0, $profileMatch.Index) + $updatedProfile + `
    $configText.Substring($profileMatch.Index + $profileMatch.Length)
[System.IO.File]::WriteAllText($resolvedConfig, $updatedConfig, [System.Text.UTF8Encoding]::new($false))

Write-Host "OCI_SESSION_PROFILE_USER_READY True"
Write-Host "The private session profile was repaired locally without printing token or user values."
