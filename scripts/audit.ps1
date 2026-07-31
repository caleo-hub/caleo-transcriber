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
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
    Invoke-Checked $python -m pip_audit
    git grep -n -E "sk-[A-Za-z0-9_-]{20,}|Bearer[[:space:]]+[A-Za-z0-9._-]{20,}" -- . ":(exclude).env.example" ":(exclude)scripts/audit.ps1"
    if ($LASTEXITCODE -eq 0) {
        throw "Padrão semelhante a secret encontrado no repositório."
    }
    if ($LASTEXITCODE -gt 1) {
        throw "Falha ao executar secret scan local."
    }
} finally {
    Pop-Location
}
