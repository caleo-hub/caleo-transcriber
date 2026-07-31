param(
    [Parameter(Mandatory = $true)]
    [string]$Executable
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$executablePath = (Resolve-Path -LiteralPath $Executable).Path
$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $executablePath
$startInfo.Arguments = "--smoke-test"
$startInfo.WorkingDirectory = Split-Path -Parent $executablePath
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
$startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$startInfo.EnvironmentVariables.Remove("PYTHONHOME")
$startInfo.EnvironmentVariables.Remove("PYTHONPATH")
$startInfo.EnvironmentVariables["PATH"] = [System.Environment]::SystemDirectory

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$process = [System.Diagnostics.Process]::Start($startInfo)
if ($null -eq $process) {
    throw "PACKAGE_SMOKE_START_FAILED"
}
if (-not $process.WaitForExit(20000)) {
    $process.Kill()
    throw "PACKAGE_SMOKE_TIMEOUT"
}
$stopwatch.Stop()
if ($process.ExitCode -ne 0) {
    throw "PACKAGE_SMOKE_EXIT_CODE_$($process.ExitCode)"
}
if ($stopwatch.Elapsed.TotalMilliseconds -lt 750) {
    throw "PACKAGE_SMOKE_EXITED_TOO_EARLY"
}

[pscustomobject]@{
    status = "ok"
    runtime = "bundled"
    external_python = $false
    elapsed_seconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 3)
} | ConvertTo-Json
