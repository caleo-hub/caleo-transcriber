# Estado da adoção

## Fase atual

Fase 6 — construir o sistema de verificação antes da autonomia.

## Resultado esperado desta fase

Mapear requisitos e riscos para verificações independentes, completar o test gauntlet e tornar os checks proporcionais bloqueadores antes de implementar a feature.

## Estado do gate

**EM ANDAMENTO.** As Fases 0–5 foram concluídas em 2026-07-31. Uma sessão nova consegue instalar, formatar, verificar, auditar e localizar fontes/limites sem acessar secrets ou serviços pagos.

## Artefatos canônicos

- `docs/adoption/INITIATIVE-BRIEF.md`
- `docs/adoption/AGENT-PERMISSIONS.md`
- `docs/adoption/RISK-REGISTER.md`
- `docs/adoption/BOOK-TRACEABILITY.md`
- `docs/adoption/STATUS.md`
- `docs/product/vision.md`
- `docs/product/prd.md`
- `docs/product/long-media-strategy.md`
- `docs/architecture/context.md`
- `docs/architecture/containers.md`
- `docs/architecture/modules.md`
- `docs/architecture/quality-attributes.md`
- `docs/adr/ADR-0001-monolito-modular-ports-adapters.md`
- `docs/adr/ADR-0002-stack-desktop-windows.md`
- `docs/adr/ADR-0003-contrato-openai-whisper.md`
- `docs/security/threat-model.md`
- `contracts/transcription-provider.md`
- `README.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `THIRD_PARTY.md`
- `pyproject.toml`
- `scripts/`
- `.github/workflows/ci.yml`
- `specs/constitution.md`
- `specs/features/FEAT-001-transcribe-single-file.md`

## Fontes lidas nesta fase

- `README.md` e `SUMMARY.md` do livro
- `guias-de-adocao/RUNBOOK-A-PRIORI-PROJETO-NOVO.md`
- `capitulos/00-introducao/03-a-pergunta-central.md`
- `capitulos/00-introducao/06-os-vinte-principios-de-controle.md`
- `capitulos/03-parte-iii-spec-driven-development-sem-teatro-documental/012-o-fluxo-completo.md`
- `capitulos/03-parte-iii-spec-driven-development-sem-teatro-documental/017-criterios-de-avanco-entre-fases.md`
- `capitulos/02-parte-ii-da-ideia-a-especificacao/006-a-especificacao-comeca-com-uma-conversa-nao-com-um-template.md`
- `capitulos/21-apendice-a-templates-reutilizaveis/a-01-visao-do-produto.md`
- `capitulos/21-apendice-a-templates-reutilizaveis/a-02-prd.md`
- `capitulos/03-parte-iii-spec-driven-development-sem-teatro-documental/013-constituicao-poucas-regras-que-realmente-governam.md`
- `capitulos/21-apendice-a-templates-reutilizaveis/a-04-constituicao-do-projeto.md`
- `capitulos/05-parte-v-o-repositorio-preparado-para-agentes/029-o-que-nunca-deve-estar-nesses-arquivos.md`
- `capitulos/02-parte-ii-da-ideia-a-especificacao/007-requisitos-que-podem-ser-verificados.md`
- `capitulos/02-parte-ii-da-ideia-a-especificacao/008-regras-de-negocio-invariantes-e-restricoes.md`
- `capitulos/02-parte-ii-da-ideia-a-especificacao/009-criterios-de-aceitacao-exemplos-e-contraexemplos.md`
- `capitulos/02-parte-ii-da-ideia-a-especificacao/010-como-detectar-uma-especificacao-fraca.md`
- `capitulos/03-parte-iii-spec-driven-development-sem-teatro-documental/014-clarificacao-o-gate-que-mais-economiza-retrabalho.md`
- `capitulos/21-apendice-a-templates-reutilizaveis/a-03-especificacao-de-feature.md`
- `capitulos/21-apendice-a-templates-reutilizaveis/a-07-criterios-de-aceitacao.md`
- `capitulos/04-parte-iv-arquitetura-como-mecanismo-de-controle/018-arquitetura-nao-e-um-desenho-bonito-e-um-conjunto-de-decisoes-que-exclui-opcoes.md`
- `capitulos/04-parte-iv-arquitetura-como-mecanismo-de-controle/019-escolha-de-estilo-comece-pelo-menor-sistema-que-sustenta-os-atributos-de-qualidade.md`
- `capitulos/04-parte-iv-arquitetura-como-mecanismo-de-controle/020-o-pacote-minimo-de-arquitetura.md`
- `capitulos/04-parte-iv-arquitetura-como-mecanismo-de-controle/021-adrs-memoria-de-decisao-nao-ata-de-reuniao.md`
- `capitulos/04-parte-iv-arquitetura-como-mecanismo-de-controle/022-fitness-functions-arquitetura-com-poder-de-veto.md`
- `capitulos/04-parte-iv-arquitetura-como-mecanismo-de-controle/023-contratos-schemas-e-fronteiras.md`
- `capitulos/21-apendice-a-templates-reutilizaveis/a-20-threat-model.md`
- `capitulos/05-parte-v-o-repositorio-preparado-para-agentes/025-o-repositorio-como-ambiente-operacional.md`
- `capitulos/05-parte-v-o-repositorio-preparado-para-agentes/026-o-que-cada-arquivo-deve-fazer.md`
- `capitulos/05-parte-v-o-repositorio-preparado-para-agentes/027-um-agents-md-completo-e-enxuto.md`
- `capitulos/05-parte-v-o-repositorio-preparado-para-agentes/028-instrucoes-por-diretorio-e-monorepos.md`
- `capitulos/07-parte-vii-instrucao-prompt-comando-skill-script-ou-mcp/037-escolha-o-mecanismo-pelo-tipo-de-problema.md`
- `capitulos/13-parte-xiii-seguranca-permissoes-e-cadeia-de-suprimentos/068-matriz-de-permissoes.md`

## Evidências disponíveis

- Requisitos iniciais fornecidos pelo responsável em 2026-07-31.
- Repositório local inicialmente sem arquivos e sem commits.
- Repositório remoto `caleo-hub/caleo-transcriber` observado como público e vazio antes do commit inicial, com branch padrão `main`.
- Perfil padrão proposto e riscos iniciais registrados antes de qualquer escolha tecnológica.
- Matriz de permissões impede código, secrets, chamadas pagas e envio de mídia nesta fase.
- Decisões humanas registradas em 2026-07-31: owner `caleo-hub`, uso pessoal, sem histórico/telemetria, dois modos no MVP, TXT/SRT selecionáveis e Windows 10.
- O README oficial do Whisper informa VRAM aproximada por modelo (1 GB em `tiny/base` até 10 GB em `large`), mas não publica mínimo formal de CPU/RAM.
- Em 2026-07-31, `caleo-hub` autorizou o envio explícito somente do áudio selecionado no modo OpenAI e aceitou o perfil padrão.
- Em 2026-07-31, `caleo-hub` aprovou todos os defaults, Windows 10 x64, a meta de três minutos e tratamento automático acima de 30 minutos.
- A estratégia tradicional foi contrastada com fontes oficiais: OpenAI limita arquivo de transcrição a 25 MB e recomenda compressão/divisão sem cortar sentenças; Whisper local usa janelas deslizantes de 30 segundos.
- Em 2026-07-31, `caleo-hub` aprovou a constituição, os required checks e a estratégia de mídia longa.
- A primeira fatia proposta reduz o fluxo a um arquivo inteiro de até 30 minutos, saída TXT e provedor previamente configurado.
- Em 2026-07-31, `caleo-hub` aprovou MP4, MP3 e WAV na primeira fatia, com extração exclusiva do áudio de vídeos, e TXT vazio com aviso para áudio silencioso.
- A primeira fatia seguirá as fronteiras da arquitetura de referência e entregará primeiro a API OpenAI com `whisper-1`; Whisper local será um adaptador opcional posterior para quem preferir evitar custo de API.
- Em 2026-07-31, `caleo-hub` aprovou aviso explicativo somente no primeiro uso da OpenAI, indicador cloud permanente e ausência de modal repetitivo; com isso, o gate da Fase 3 foi atendido.
- A proposta da Fase 4 define monólito modular com ports-and-adapters, Python/PySide6, FFmpeg, Credential Manager, PyInstaller `onedir`, contrato `whisper-1`, fitness functions e threat model.
- A documentação oficial da OpenAI limita uploads de transcrição a 25 MB, recomenda compressão ou divisão para entradas maiores e informa que timestamps por segmento de `whisper-1` não adicionam latência.
- Em 2026-07-31, `caleo-hub` aprovou integralmente as cinco decisões da Fase 4: estilo e fronteiras, stack, contrato OpenAI, compra versus construção e risco residual do threat model.
- O harness usa Python 3.12.10 local, dependências diretas fixadas, `.venv`, comandos `.cmd`/PowerShell, Ruff, mypy, Import Linter, pytest, build, pip-audit e CI Windows.
- `.\verify.cmd` passou: formatação, lint, tipos, três contratos de dependência, dois testes, build de sdist/wheel e `pip check`.
- `.\audit.cmd` passou sem vulnerabilidades conhecidas; o pacote local `caleo-transcriber` foi corretamente ignorado por não existir no PyPI.
- O caminho com caracteres acentuados expôs uma incompatibilidade de encoding no `pip-audit`; o script agora força UTF-8 e foi revalidado.
- A chave OpenAI permanece fora de `.env.example`; a UI futura usará o Windows Credential Manager por `CredentialStore`.

## Fatos observados

- O produto alvo é um executável Windows com interface gráfica.
- Há dois modos desejados: OpenAI API e Whisper local.
- Há necessidade de lote, intervalo, destino de saída e progresso.
- A credencial deve ser configurada uma vez.
- Não haverá histórico persistente nem telemetria.
- O MVP incluirá os modos OpenAI e Whisper local, em incrementos: OpenAI primeiro e local depois.
- TXT e SRT serão opções selecionáveis e Windows 10 será o mínimo.

## Inferências, hipóteses e desconhecidos

- **Inferência:** o usuário primário não deve precisar de terminal.
- **Decisão:** o perfil padrão é proporcional ao risco aceito.
- **Decisão:** o uso inicial é pessoal.
- **Decisão:** não haverá histórico persistente ou telemetria.
- **Desconhecido:** idiomas, timestamps, locutores e métricas de qualidade.
- **Desconhecido:** mínimo de CPU/RAM e desempenho aceitável do modo local; a fonte oficial só quantifica VRAM.
- **Decisão:** o modo OpenAI pode enviar somente o áudio selecionado, após ação explícita.

## Decisões humanas pendentes

Nenhuma decisão humana bloqueia o harness. A escolha do build de FFmpeg e suas obrigações de licença permanece deliberadamente bloqueada antes de vendorização/release.

## Riscos e bloqueios

- Segredo persistente e repositório público.
- Possível envio de conteúdo sensível a serviço externo.
- Custo de API e consumo local imprevisíveis sem limites.
- PySide6 e PyInstaller tiveram licenças identificadas; o build concreto de FFmpeg ainda exige origem, versão, checksum e revisão LGPL/GPL antes de ser incorporado.
- Chunking e paralelismo exigem contrato de contexto, overlap, recomposição, checkpoints e limites de recurso.

## Próxima ação recomendada

Executar a Fase 6: criar o plano de testes e ampliar o gauntlet de requisitos/riscos sem usar chave, rede ou mídia pessoal.
