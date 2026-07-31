# TASK-022 — Patch beta 0.2.1

## Objetivo

Publicar uma nova beta Windows x64 contendo a correção de contraste e o diagnóstico acionável da
TASK-021, sem substituir ou apagar a beta anterior.

## Contexto e fontes

O owner autorizou em 2026-07-31 a correção do falso positivo de CI e uma nova release funcional.
Aplicam-se TASK-019/021, o runbook de release, o alvo de distribuição e o rollback Windows.

## Escopo de arquivos

- versão de runtime, pacote, recurso Windows, workflow e documentação em `0.2.1`;
- tag e prerelease `v0.2.1-beta.1`;
- instalador x64, checksum, SBOM, licenças, notas e evidência de build;
- correção do scanner para diferenciar uma chave `sk-…` do trecho interno em `task-…`.

## Restrições e autonomia

Somente mídia sintética nos smokes. O vídeo pessoal informado não será enviado. A release permanece
sem Authenticode e nenhuma instalação local é executada sem autorização separada. A chave recusada
não entra no repositório nem no pacote.

## Critérios de aceitação

1. O auditor detecta um prefixo `sk-` em posição de token, mas não marca `task-021` como segredo.
2. Runtime, metadata Windows, workflow e candidato usam `0.2.1` de forma consistente.
3. `format.cmd`, `verify.cmd`, `audit.cmd`, gitleaks e pacote remoto passam.
4. O candidato final é construído do commit mesclado em `main` e passa inspeção, smoke e preflight.
5. A prerelease contém instalador, checksum, SBOM, licenças, notas e evidência do build.
6. O instalador baixado do GitHub possui o mesmo SHA-256 publicado e não é executado localmente.
7. `v0.2.0-beta.1` permanece disponível como rollback.

## Validação e evidência

Checks locais/remotos, `build-evidence.json`, `SHA256SUMS.txt`, digest do asset publicado e
verificação pós-download controlada.

## Rollback

Marcar o patch como não recomendado e orientar reinstalação de `v0.2.0-beta.1`; preservar tags,
evidências, credencial protegida e saídas TXT/SRT.

## Resultado

Concluída em 2026-07-31 pela PR #17. O tag `v0.2.1-beta.1` aponta para `1b01f3d`, contém os seis
assets previstos e o instalador baixado passou pelo preflight com SHA-256
`c079f478cf5833d6c7ac589f16c789aaf3ed80c38035289a6c89e6ec095f99a6`. Nenhuma instalação local
ou mídia pessoal foi usada na validação da release.
