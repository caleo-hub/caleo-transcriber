param(
    [string]$Destination = (Join-Path (Split-Path -Parent $PSScriptRoot) "vendor\ffmpeg\bin"),
    [switch]$Extract
)

$ErrorActionPreference = "Stop"

$releaseTag = "autobuild-2026-07-31-14-10"
$archiveName = "ffmpeg-n8.1.2-34-g9b6c8969e0-win64-lgpl-8.1.zip"
$expectedBytes = 145349121
$expectedSha256 = "089e4169e93b2b3f3acbfced3c0704d24276a225641bdda04d796d28b07a2a38"
$downloadUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/$releaseTag/$archiveName"

function Get-Sha256([string]$Path) {
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $stream = [System.IO.File]::OpenRead($Path)
        try {
            $bytes = $sha256.ComputeHash($stream)
            return [System.BitConverter]::ToString($bytes).Replace("-", "").ToLowerInvariant()
        }
        finally {
            $stream.Dispose()
        }
    }
    finally {
        $sha256.Dispose()
    }
}

$resolvedDestination = [System.IO.Path]::GetFullPath($Destination)
[System.IO.Directory]::CreateDirectory($resolvedDestination) | Out-Null
$archivePath = Join-Path $resolvedDestination $archiveName
$partialPath = "$archivePath.download"

if (-not (Test-Path -LiteralPath $archivePath -PathType Leaf)) {
    try {
        Invoke-WebRequest -UseBasicParsing -Uri $downloadUrl -OutFile $partialPath
        Move-Item -LiteralPath $partialPath -Destination $archivePath
    }
    finally {
        Remove-Item -LiteralPath $partialPath -Force -ErrorAction SilentlyContinue
    }
}

$actualBytes = (Get-Item -LiteralPath $archivePath).Length
if ($actualBytes -ne $expectedBytes) {
    throw "FFMPEG_SIZE_MISMATCH"
}

$actualSha256 = Get-Sha256 $archivePath
if ($actualSha256 -ne $expectedSha256) {
    throw "FFMPEG_SHA256_MISMATCH"
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($archivePath)
try {
    $entryNames = @($zip.Entries | ForEach-Object { $_.FullName })
    if (-not ($entryNames | Where-Object { $_ -like "*/bin/ffmpeg.exe" })) {
        throw "FFMPEG_EXECUTABLE_MISSING"
    }
    if (-not ($entryNames | Where-Object { $_ -like "*/bin/ffprobe.exe" })) {
        throw "FFPROBE_EXECUTABLE_MISSING"
    }
}
finally {
    $zip.Dispose()
}

if ($Extract) {
    $extractPath = Join-Path $resolvedDestination "ffmpeg-8.1.2-lgpl"
    if (Test-Path -LiteralPath $extractPath) {
        throw "FFMPEG_EXTRACT_TARGET_EXISTS"
    }
    Expand-Archive -LiteralPath $archivePath -DestinationPath $extractPath
}

[pscustomobject]@{
    version = "8.1.2-34-g9b6c8969e0"
    release_tag = $releaseTag
    license = "LGPL-3.0-or-later"
    archive = $archivePath
    bytes = $actualBytes
    sha256 = $actualSha256
    extracted = [bool]$Extract
} | ConvertTo-Json
