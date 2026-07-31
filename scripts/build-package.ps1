param(
    [ValidatePattern('^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$')]
    [string]$Version = "0.2.1",

    [switch]$RealOpenAISmoke,

    [switch]$RealOpenAISmokeCredentialRejected
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ($RealOpenAISmoke -and $RealOpenAISmokeCredentialRejected) {
    throw "PACKAGE_OPENAI_SMOKE_STATE_CONFLICT"
}

$projectRoot = (Resolve-Path (Split-Path -Parent $PSScriptRoot)).Path
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$pyinstaller = Join-Path $projectRoot ".venv\Scripts\pyinstaller.exe"
$packageBase = Join-Path $projectRoot "build\package"
$packageRoot = Join-Path $packageBase "CaleoTranscriber"
$pyinstallerWork = Join-Path $projectRoot "build\pyinstaller"
$candidateRoot = Join-Path $projectRoot "artifacts\candidate\$Version"
$rollbackRoot = Join-Path $projectRoot "build\rollback"
$installerName = "CaleoTranscriber-Setup-$Version-x64.exe"

function Reset-ControlledDirectory([string]$Path, [string]$AllowedParent) {
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $fullParent = [System.IO.Path]::GetFullPath($AllowedParent).TrimEnd('\') + '\'
    if (-not $fullPath.StartsWith($fullParent, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "PACKAGE_UNSAFE_CLEAN_TARGET"
    }
    if (Test-Path -LiteralPath $fullPath) {
        Remove-Item -LiteralPath $fullPath -Recurse -Force
    }
    [System.IO.Directory]::CreateDirectory($fullPath) | Out-Null
}

if (-not (Test-Path -LiteralPath $python) -or -not (Test-Path -LiteralPath $pyinstaller)) {
    throw "PACKAGE_TOOLCHAIN_MISSING"
}
$sourceVersion = & $python -c "import caleo_transcriber; print(caleo_transcriber.__version__)"
if ($LASTEXITCODE -ne 0 -or $sourceVersion.Trim() -ne $Version) {
    throw "PACKAGE_VERSION_MISMATCH"
}

& (Join-Path $projectRoot "scripts\fetch-ffmpeg.ps1") -Extract | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "PACKAGE_FFMPEG_FETCH_FAILED"
}
$ffmpegRoots = @(
    Get-ChildItem (Join-Path $projectRoot "vendor\ffmpeg\bin\ffmpeg-8.1.2-lgpl") `
        -Directory -Recurse |
        Where-Object {
            (Test-Path -LiteralPath (Join-Path $_.FullName "ffmpeg.exe")) -and
            (Test-Path -LiteralPath (Join-Path $_.FullName "ffprobe.exe"))
        }
)
if ($ffmpegRoots.Count -ne 1) {
    throw "PACKAGE_FFMPEG_LAYOUT_INVALID"
}
$ffmpegBin = $ffmpegRoots[0].FullName
$ffmpegDistribution = Split-Path -Parent $ffmpegBin
$ffmpegLicense = Join-Path $ffmpegDistribution "LICENSE.txt"
if (-not (Test-Path -LiteralPath $ffmpegLicense)) {
    throw "PACKAGE_FFMPEG_LICENSE_MISSING"
}

Reset-ControlledDirectory $packageBase (Join-Path $projectRoot "build")
Reset-ControlledDirectory $pyinstallerWork (Join-Path $projectRoot "build")
Reset-ControlledDirectory $candidateRoot (Join-Path $projectRoot "artifacts\candidate")
Reset-ControlledDirectory $rollbackRoot (Join-Path $projectRoot "build")

$commit = (& git -C $projectRoot rev-parse HEAD).Trim()
$commitDate = (& git -C $projectRoot show -s --format=%cI HEAD).Trim()
$created = [DateTimeOffset]::Parse($commitDate).UtcDateTime.ToString("yyyy-MM-ddTHH:mm:ssZ")
$env:PYTHONHASHSEED = "0"
$env:SOURCE_DATE_EPOCH = [DateTimeOffset]::Parse($commitDate).ToUnixTimeSeconds().ToString()

$buildTimer = [System.Diagnostics.Stopwatch]::StartNew()
& $pyinstaller `
    --noconfirm `
    --clean `
    --distpath $packageBase `
    --workpath $pyinstallerWork `
    (Join-Path $projectRoot "packaging\CaleoTranscriber.spec")
if ($LASTEXITCODE -ne 0) {
    throw "PACKAGE_PYINSTALLER_FAILED"
}

$ffmpegTarget = Join-Path $packageRoot "ffmpeg"
$licensesTarget = Join-Path $packageRoot "licenses"
[System.IO.Directory]::CreateDirectory($ffmpegTarget) | Out-Null
[System.IO.Directory]::CreateDirectory($licensesTarget) | Out-Null
Copy-Item -LiteralPath (Join-Path $ffmpegBin "ffmpeg.exe") -Destination $ffmpegTarget
Copy-Item -LiteralPath (Join-Path $ffmpegBin "ffprobe.exe") -Destination $ffmpegTarget
Copy-Item -LiteralPath $ffmpegLicense -Destination (Join-Path $licensesTarget "LGPL-3.0.txt")
Copy-Item -LiteralPath (Join-Path $projectRoot "THIRD_PARTY.md") -Destination $packageRoot

$sbomPath = Join-Path $candidateRoot "sbom.spdx.json"
& $python (Join-Path $projectRoot "scripts\generate-sbom.py") `
    --version $Version `
    --commit $commit `
    --created $created `
    --output $sbomPath `
    --licenses-dir (Join-Path $licensesTarget "python")
if ($LASTEXITCODE -ne 0) {
    throw "PACKAGE_SBOM_FAILED"
}
Copy-Item -LiteralPath $sbomPath -Destination (Join-Path $packageRoot "sbom.spdx.json")

$releaseNotes = (
    Get-Content -LiteralPath (Join-Path $projectRoot "packaging\RELEASE_NOTES.md") -Raw
).Replace("{{VERSION}}", $Version)
$releaseNotesPath = Join-Path $candidateRoot "RELEASE_NOTES.md"
[System.IO.File]::WriteAllText($releaseNotesPath, $releaseNotes, [System.Text.UTF8Encoding]::new($false))
Copy-Item -LiteralPath $releaseNotesPath -Destination $packageRoot
Copy-Item -LiteralPath (Join-Path $projectRoot "THIRD_PARTY.md") -Destination $candidateRoot

& $python (Join-Path $projectRoot "scripts\inspect-package.py") `
    $packageRoot `
    --forbidden-path-fragment $projectRoot
if ($LASTEXITCODE -ne 0) {
    throw "PACKAGE_INSPECTION_FAILED"
}
$smokeJson = & (Join-Path $projectRoot "scripts\smoke-package.ps1") `
    -Executable (Join-Path $packageRoot "CaleoTranscriber.exe")
if ($LASTEXITCODE -ne 0) {
    throw "PACKAGE_SMOKE_FAILED"
}
$smoke = $smokeJson | ConvertFrom-Json

$isccCandidates = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
    (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe")
)
$iscc = $isccCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ($null -eq $iscc) {
    throw "PACKAGE_INNO_SETUP_MISSING"
}

& $iscc `
    "/Qp" `
    "/DAppVersion=$Version" `
    "/DSourceDir=$packageRoot" `
    "/DOutputDir=$candidateRoot" `
    (Join-Path $projectRoot "packaging\CaleoTranscriber.iss")
if ($LASTEXITCODE -ne 0) {
    throw "PACKAGE_INNO_COMPILE_FAILED"
}
$installerPath = Join-Path $candidateRoot $installerName
if (-not (Test-Path -LiteralPath $installerPath)) {
    throw "PACKAGE_INSTALLER_MISSING"
}
& $python (Join-Path $projectRoot "scripts\inspect-pe-signature.py") `
    $installerPath `
    --expect-unsigned
if ($LASTEXITCODE -ne 0) {
    throw "PACKAGE_UNEXPECTED_SIGNATURE_STATE"
}

$hashBeforeRollback = (Get-FileHash -Algorithm SHA256 -LiteralPath $installerPath).Hash.ToLowerInvariant()
$rollbackTimer = [System.Diagnostics.Stopwatch]::StartNew()
$withdrawnPath = Join-Path $rollbackRoot $installerName
Move-Item -LiteralPath $installerPath -Destination $withdrawnPath
if (Test-Path -LiteralPath $installerPath) {
    throw "PACKAGE_ROLLBACK_WITHDRAW_FAILED"
}
Move-Item -LiteralPath $withdrawnPath -Destination $installerPath
$rollbackTimer.Stop()
$hashAfterRollback = (Get-FileHash -Algorithm SHA256 -LiteralPath $installerPath).Hash.ToLowerInvariant()
if ($hashBeforeRollback -ne $hashAfterRollback) {
    throw "PACKAGE_ROLLBACK_DIGEST_CHANGED"
}

$checksumPath = Join-Path $candidateRoot "SHA256SUMS.txt"
[System.IO.File]::WriteAllText(
    $checksumPath,
    "$hashAfterRollback *$installerName`n",
    [System.Text.UTF8Encoding]::new($false)
)
$buildTimer.Stop()

$evidence = [ordered]@{
    schema_version = 1
    version = $Version
    commit = $commit
    installer = $installerName
    sha256 = $hashAfterRollback
    installer_bytes = (Get-Item -LiteralPath $installerPath).Length
    package_bytes = (
        Get-ChildItem -LiteralPath $packageRoot -Recurse -File |
        Measure-Object -Property Length -Sum
    ).Sum
    package_smoke_seconds = $smoke.elapsed_seconds
    build_seconds = [Math]::Round($buildTimer.Elapsed.TotalSeconds, 3)
    rollback_rehearsal = "withdraw-and-restore-unpublished-candidate"
    rollback_seconds = [Math]::Round($rollbackTimer.Elapsed.TotalSeconds, 3)
    authenticode = "not-signed"
    real_openai_call = if ($RealOpenAISmokeCredentialRejected) {
        "attempted-with-synthetic-audio-credential-rejected"
    } elseif ($RealOpenAISmoke) {
        "run-once-with-synthetic-audio-owner-approved"
    } else {
        "not-run-approval-required"
    }
    windows_10_clean_vm = "not-run-owner-environment-required"
}
$evidence | ConvertTo-Json | Set-Content `
    -LiteralPath (Join-Path $candidateRoot "build-evidence.json") -Encoding utf8

& (Join-Path $projectRoot "release-preflight.cmd") `
    -Version $Version `
    -CandidateDirectory $candidateRoot
if ($LASTEXITCODE -ne 0) {
    throw "PACKAGE_PREFLIGHT_FAILED"
}

$evidence | ConvertTo-Json
