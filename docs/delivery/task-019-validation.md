# Evidência TASK-019 — beta 0.2.0

- Data: 2026-07-31
- Owner: `caleo-hub`
- Tag planejada: `v0.2.0-beta.1`
- Plataforma local: Windows x64

## Gauntlet

- `verify.cmd`: aprovado com 173 testes antes do bump; nova execução final exigida no commit candidato;
- arquitetura: 3 contratos mantidos, 0 quebrado;
- evidência UX: vazio, execução, falha parcial e retomada em `docs/evidence/ux-increment-2/`;
- ícone: PNG RGBA e ICO com 16/24/32/48/64/128/256 px;
- segredo em `.env.example`: diff vazio; chave somente no Windows Credential Manager.

## Smoke OpenAI autorizado

- autorização do owner: até 5 chamadas;
- executadas: 1;
- mídia: voz sintética gerada localmente, sem conteúdo pessoal;
- resultado: sucesso, 5.740 ms, 1 segmento;
- texto e áudio: não registrados; temporários removidos;
- chamadas autorizadas restantes: 4.

## Gates ainda declarados

- Authenticode: não assinado; risco visível nas notas da beta;
- instalação/desinstalação local: não executada, pois não foi autorizada;
- VM Windows 10 x64 limpa: não disponível neste ambiente;
- publicação: autorizada somente como GitHub prerelease beta após preflight/checks verdes.

## Critério de promoção

O mesmo digest produzido pelo commit candidato deve passar `audit.cmd`, build, smoke empacotado,
preflight e checks do GitHub. A release será marcada como pré-lançamento e manterá checksum, SBOM,
licenças e notas junto ao instalador.
