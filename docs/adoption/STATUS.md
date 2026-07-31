# Estado da adoção

## Fase atual

Fase 1 — descobrir o problema e o resultado esperado.

## Resultado esperado desta fase

Aprovar visão, atores, resultados mensuráveis, primeira fatia, não objetivos, hipóteses e restrições sem antecipar arquitetura.

## Estado do gate

**NÃO ATENDIDO.** A Fase 0 foi aprovada em 2026-07-31. A visão e o PRD da Fase 1 estão em revisão e contêm decisões de comportamento ainda abertas.

## Artefatos canônicos

- `docs/adoption/INITIATIVE-BRIEF.md`
- `docs/adoption/AGENT-PERMISSIONS.md`
- `docs/adoption/RISK-REGISTER.md`
- `docs/adoption/BOOK-TRACEABILITY.md`
- `docs/adoption/STATUS.md`
- `docs/product/vision.md`
- `docs/product/prd.md`

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

## Evidências disponíveis

- Requisitos iniciais fornecidos pelo responsável em 2026-07-31.
- Repositório local inicialmente sem arquivos e sem commits.
- Repositório remoto `caleo-hub/caleo-transcriber` observado como público e vazio antes do commit inicial, com branch padrão `main`.
- Perfil padrão proposto e riscos iniciais registrados antes de qualquer escolha tecnológica.
- Matriz de permissões impede código, secrets, chamadas pagas e envio de mídia nesta fase.
- Decisões humanas registradas em 2026-07-31: owner `caleo-hub`, uso pessoal, sem histórico/telemetria, dois modos no MVP, TXT/SRT selecionáveis e Windows 10.
- O README oficial do Whisper informa VRAM aproximada por modelo (1 GB em `tiny/base` até 10 GB em `large`), mas não publica mínimo formal de CPU/RAM.
- Em 2026-07-31, `caleo-hub` autorizou o envio explícito somente do áudio selecionado no modo OpenAI e aceitou o perfil padrão.

## Fatos observados

- O produto alvo é um executável Windows com interface gráfica.
- Há dois modos desejados: OpenAI API e Whisper local.
- Há necessidade de lote, intervalo, destino de saída e progresso.
- A credencial deve ser configurada uma vez.
- Não haverá histórico persistente nem telemetria.
- O primeiro MVP incluirá os modos OpenAI e Whisper local.
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

1. Aceitar ou corrigir os defaults de produto propostos em `docs/product/prd.md`.
2. Definir os critérios de saída do discovery que ainda estão marcados como propostas.

## Riscos e bloqueios

- Segredo persistente e repositório público.
- Possível envio de conteúdo sensível a serviço externo.
- Custo de API e consumo local imprevisíveis sem limites.
- Dependências nativas e distribuição de binário ainda não avaliadas.

## Próxima ação recomendada

O responsável humano revisa visão, PRD e defaults propostos. Com o gate da Fase 1 aceito, iniciar a constituição do projeto; não gerar scaffold ou código de produto antes disso.
