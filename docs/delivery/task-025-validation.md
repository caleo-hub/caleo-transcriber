# Validação da TASK-025 e release 0.3.2

## Evidência local

- `format.cmd`: aprovado.
- `verify.cmd`: 198 testes aprovados, lint, tipos, contratos, build de sdist/wheel e `pip check`.
- `audit.cmd`: nenhuma vulnerabilidade conhecida nas dependências auditáveis.
- Testes específicos cobrem fila com diretórios mistos, nome `_transcription`, TXT/SRT, colisões,
  checkbox acessível e abertura da pasta efetiva.

## Evidência remota

- PR #23: implementação mesclada no commit `7b76694621040e3fabe0616bc0f14df49b77e27c`; `verify`,
  `package` e `gitleaks` aprovados.
- PR #24: versionamento 0.3.2 mesclado no commit `f3db407ea90b0719b21a06ee5ddaedbac2f94e8b`;
  `verify`, `package` e `gitleaks` aprovados.
- Tag `v0.3.2-beta.1`: prerelease pública, não draft, com seis assets.
- Instalador: `CaleoTranscriber-Setup-0.3.2-x64.exe`, 114.183.317 bytes, SHA-256
  `6964a6d4847aa5cf05d6423745a666dc225c5b9f0030c2f7bd682db5dcbef9de`.
- Pós-download: `release-preflight.ps1` aprovou versão 0.3.2, checksum e estrutura do instalador.

## Limites e rollback

O instalador não possui assinatura Authenticode e pode acionar o SmartScreen. Nenhuma instalação
local, chamada OpenAI ou mídia pessoal foi usada. O rollback recomendado é `v0.3.1-beta.1`.
