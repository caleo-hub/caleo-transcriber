$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$expectedVersion = "6.7.3"
$expectedSha256 = "9c73c3bae7ed48d44112a0f48e66742c00090bdb5bef71d9d3c056c66e97b732"
$downloadUrl = "https://github.com/jrsoftware/issrc/releases/download/is-6_7_3/innosetup-6.7.3.exe"
$installRoot = Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6"
$compiler = Join-Path $installRoot "ISCC.exe"

$installed = Get-ItemProperty HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* `
    -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -like "Inno Setup*" } |
    Select-Object -First 1
if ($null -ne $installed) {
    if ($installed.DisplayVersion -ne $expectedVersion -or -not (Test-Path -LiteralPath $compiler)) {
        throw "INNO_SETUP_VERSION_CONFLICT"
    }
    Write-Output "inno-setup: ok version=$expectedVersion source=existing"
    exit 0
}

$downloadRoot = Join-Path ([System.IO.Path]::GetTempPath()) "caleo-inno-6.7.3"
[System.IO.Directory]::CreateDirectory($downloadRoot) | Out-Null
$installer = Join-Path $downloadRoot "innosetup-6.7.3.exe"
Invoke-WebRequest -UseBasicParsing -Uri $downloadUrl -OutFile $installer

$actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $installer).Hash.ToLowerInvariant()
if ($actualHash -ne $expectedSha256) {
    throw "INNO_SETUP_SHA256_MISMATCH"
}
$signature = Get-AuthenticodeSignature -LiteralPath $installer
if ($signature.Status -ne [System.Management.Automation.SignatureStatus]::Valid) {
    throw "INNO_SETUP_SIGNATURE_INVALID"
}
if ($signature.SignerCertificate.Subject -notlike "CN=Pyrsys B.V.*") {
    throw "INNO_SETUP_SIGNER_INVALID"
}

$process = Start-Process -FilePath $installer `
    -ArgumentList "/VERYSILENT", "/CURRENTUSER", "/NORESTART", "/SUPPRESSMSGBOXES" `
    -Wait -PassThru -WindowStyle Hidden
if ($process.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $compiler)) {
    throw "INNO_SETUP_INSTALL_FAILED"
}
Write-Output "inno-setup: ok version=$expectedVersion source=verified-download"
