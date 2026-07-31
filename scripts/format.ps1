$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

function Invoke-Checked {
    param([string]$Command, [Parameter(ValueFromRemainingArguments)][string[]]$CommandArgs)
    & $Command @CommandArgs
    if ($LASTEXITCODE -ne 0) { throw "Comando falhou com código $LASTEXITCODE" }
}

if (-not (Test-Path -LiteralPath $python)) {
    throw "Ambiente ausente. Execute .\scripts\setup.ps1"
}

Push-Location $projectRoot
try {
    Invoke-Checked $python -m ruff format src tests
    Invoke-Checked $python -m ruff check --fix src tests
} finally {
    Pop-Location
}
