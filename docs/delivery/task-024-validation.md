# Validação da TASK-024

## Evidência local

- `format.cmd`: 70 arquivos formatados.
- `verify.cmd`: Ruff, mypy, três contratos de importação e 192 testes aprovados.
- `audit.cmd`: nenhuma vulnerabilidade conhecida nas dependências auditáveis.
- Regressão: teste confirma `QMenu` real, seleção, itens desabilitados e separador com cores explícitas.
- UX: `docs/evidence/ux-increment-2/07-clear-menu.png` mostra estados normal, selecionado e
  desabilitado sob paleta controlada.
- Rede: nenhuma chamada OpenAI, chave ou mídia utilizada.

## Evidência de release

- PR #21: `verify`, gitleaks e `package` aprovados; squash merge no commit
  `140e896af435ce553555701ed699c019152dc9fd`.
- Tag: `v0.3.1-beta.1`, prerelease pública e não draft, apontando para o commit integrado.
- Assets: seis arquivos publicados, incluindo instalador, checksum, SBOM, licenças, notas e
  evidência de build.
- Instalador: `CaleoTranscriber-Setup-0.3.1-x64.exe`, 114.188.486 bytes, SHA-256
  `feeb3de9dc1b6a17b83f10a6f1c860cf95a40fe17c9c5d88d39220d37b0eb67a`.
- Pós-download: `release-preflight.ps1` aprovou versão, checksum, arquitetura e estrutura do
  instalador baixado da release.
- Segurança operacional: pacote não assinado; nenhuma instalação, mídia pessoal ou chamada
  OpenAI foi executada. `v0.3.0-beta.1` permanece disponível para rollback.
