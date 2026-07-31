$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

function Invoke-Checked {
    param([string]$Command, [Parameter(ValueFromRemainingArguments)][string[]]$CommandArgs)
    & $Command @CommandArgs
    if ($LASTEXITCODE -ne 0) { throw "Comando falhou com código $LASTEXITCODE" }
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    py -3.12 -m venv $venvPath
}

Invoke-Checked $venvPython -m pip install --upgrade "pip==26.2"
Invoke-Checked $venvPython -m pip install --editable "$projectRoot[dev]"
Invoke-Checked $venvPython -m pip check

Write-Host "Setup concluído. Execute .\scripts\verify.ps1"
