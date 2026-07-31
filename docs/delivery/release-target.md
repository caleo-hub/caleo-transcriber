# Alvo de distribuição

- **Decisão do owner:** 2026-07-31
- **Canal:** GitHub Releases de `caleo-hub/caleo-transcriber`
- **Plataforma:** Windows 10/11 x64
- **Estado atual:** `v0.2.1-beta.1` publicada; `v0.3.0-beta.1` autorizada pelo owner

## Artefato principal

`CaleoTranscriber-Setup-<versão>-x64.exe`: instalador que inclui aplicativo, Python, Qt e dependências nativas aprovadas. Após instalar, o programa aparece no menu Iniciar e funciona sem terminal ou ambiente de desenvolvimento.

## Artefatos complementares

- `SHA256SUMS.txt` para integridade;
- notas de release com requisitos, mudanças, riscos conhecidos e rollback;
- ZIP portátil opcional, sem substituir o instalador principal;
- SBOM e avisos de licenças quando a release for preparada.
- `RELEASE_NOTES.md` com decisão pós-validação e instruções de rollback.

## Gate de publicação

1. CI, testes, auditoria e build passam no commit tagueado;
2. instalador é produzido em runner Windows a partir de versões travadas;
3. checksum é calculado após o build e publicado junto ao artefato;
4. o arquivo baixado do GitHub Release é instalado e testado em VM Windows 10 x64 limpa;
5. chave não está no pacote e é criada somente pela UI no Credential Manager;
6. FFmpeg possui origem, checksum e licença registrados;
7. owner aprova a release.

O fluxo completo e a adaptação de rollout estão em `release-runbook.md`; observabilidade em
`observability.md`; recuperação em `rollback-runbook.md`.

## Assinatura

Assinatura Authenticode é recomendada para reduzir alertas do SmartScreen, mas requer certificado e processo de proteção da chave de assinatura. A decisão entre release inicialmente não assinada ou aquisição de certificado será tomada antes da primeira publicação pública.
