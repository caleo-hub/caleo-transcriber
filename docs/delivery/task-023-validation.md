# Validação da TASK-023

## Evidência local

- `format.cmd`: 70 arquivos formatados.
- `verify.cmd`: Ruff, mypy, três contratos de importação e 191 testes aprovados.
- `audit.cmd`: nenhuma vulnerabilidade conhecida nas dependências auditáveis.
- UX: `docs/evidence/ux-increment-2/06-queue-controls.png`, gerada sem rede ou mídia.
- Segurança: remoção/limpeza exercitadas sem chamadas ao filesystem; ativo nunca é removido.
- Concorrência: pausa preserva pendentes; cancelar atual não cancela o restante; um ativo mantido.
- Rede: nenhuma chamada OpenAI e nenhuma mídia pessoal utilizada.

## Evidência de release

- PR #19: `verify`, `gitleaks` e `package` aprovados.
- Commit da release: `92270095b3225be0465ca2a9732b2171469774ff`.
- Tag: `v0.3.0-beta.1`, prerelease pública e não draft.
- Seis assets: instalador, checksum, SBOM, licenças, notas e evidência de build.
- Instalador: `CaleoTranscriber-Setup-0.3.0-x64.exe`, 114.172.269 bytes.
- SHA-256: `3175f209626c283ce2d5ef09bfbbc1da79aab0cd6fb34e05b58de2d5cd12acb5`.
- Preflight pós-download aprovado sem executar ou instalar o aplicativo.
- Build x64 e smoke aprovados; Authenticode ausente e declarado nas notas.
- Rollback: `v0.2.1-beta.1` permanece publicada.
