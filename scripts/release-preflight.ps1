param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$')]
    [string]$Version,

    [Parameter(Mandatory = $true)]
    [string]$CandidateDirectory
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not (Test-Path -LiteralPath $CandidateDirectory -PathType Container)) {
    throw "PREFLIGHT_CANDIDATE_NOT_FOUND: Diretório candidato não encontrado"
}

$candidatePath = (Resolve-Path -LiteralPath $CandidateDirectory).Path
$installerName = "CaleoTranscriber-Setup-$Version-x64.exe"
$requiredFiles = @(
    $installerName,
    "SHA256SUMS.txt",
    "sbom.spdx.json",
    "THIRD_PARTY.md",
    "RELEASE_NOTES.md"
)

foreach ($fileName in $requiredFiles) {
    $filePath = Join-Path $candidatePath $fileName
    if (-not (Test-Path -LiteralPath $filePath -PathType Leaf)) {
        throw "PREFLIGHT_MISSING_FILE: Artefato obrigatório ausente: $fileName"
    }
    if ((Get-Item -LiteralPath $filePath).Length -eq 0) {
        throw "PREFLIGHT_EMPTY_FILE: Artefato obrigatório vazio: $fileName"
    }
}

$sbomPath = Join-Path $candidatePath "sbom.spdx.json"
try {
    Get-Content -LiteralPath $sbomPath -Raw | ConvertFrom-Json | Out-Null
} catch {
    throw "PREFLIGHT_INVALID_SBOM: sbom.spdx.json não contém JSON válido"
}

$expectedHash = $null
$checksumPath = Join-Path $candidatePath "SHA256SUMS.txt"
foreach ($line in Get-Content -LiteralPath $checksumPath) {
    if ($line -match '^(?<hash>[A-Fa-f0-9]{64})\s+\*?(?<file>.+)$') {
        if ($Matches.file -eq $installerName) {
            $expectedHash = $Matches.hash.ToLowerInvariant()
            break
        }
    }
}

if ($null -eq $expectedHash) {
    throw "PREFLIGHT_MISSING_CHECKSUM: SHA256SUMS.txt não contém entrada válida para $installerName"
}

$installerPath = Join-Path $candidatePath $installerName
$actualHash = (Get-FileHash -LiteralPath $installerPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualHash -ne $expectedHash) {
    throw "PREFLIGHT_CHECKSUM_MISMATCH: Checksum SHA-256 divergente para $installerName"
}

Write-Output "release-preflight: ok version=$Version sha256=$actualHash"
