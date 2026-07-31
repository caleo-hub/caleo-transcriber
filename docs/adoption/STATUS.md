# Estado da adoção

## Fase atual

Fase 0 — abrir a iniciativa sem abrir o editor de código.

## Resultado esperado desta fase

Ter owner humano, problema inicial compreensível, perfil de risco aceito, contextos `BOOK_ROOT`/`PROJECT_ROOT` e limites de permissão explícitos.

## Estado do gate

**NÃO ATENDIDO.** Owners, uso pessoal e recorte principal foram confirmados. Restam a política mínima de transferência exigida pelo modo OpenAI e o aceite do perfil padrão.

## Artefatos canônicos

- `docs/adoption/INITIATIVE-BRIEF.md`
- `docs/adoption/AGENT-PERMISSIONS.md`
- `docs/adoption/RISK-REGISTER.md`
- `docs/adoption/BOOK-TRACEABILITY.md`
- `docs/adoption/STATUS.md`

## Fontes lidas nesta fase

- `README.md` e `SUMMARY.md` do livro
- `guias-de-adocao/RUNBOOK-A-PRIORI-PROJETO-NOVO.md`
- `capitulos/00-introducao/03-a-pergunta-central.md`
- `capitulos/00-introducao/06-os-vinte-principios-de-controle.md`
- `capitulos/03-parte-iii-spec-driven-development-sem-teatro-documental/012-o-fluxo-completo.md`
- `capitulos/03-parte-iii-spec-driven-development-sem-teatro-documental/017-criterios-de-avanco-entre-fases.md`

## Evidências disponíveis

- Requisitos iniciais fornecidos pelo responsável em 2026-07-31.
- Repositório local inicialmente sem arquivos e sem commits.
- Repositório remoto `caleo-hub/caleo-transcriber` observado como público e vazio antes do commit inicial, com branch padrão `main`.
- Perfil padrão proposto e riscos iniciais registrados antes de qualquer escolha tecnológica.
- Matriz de permissões impede código, secrets, chamadas pagas e envio de mídia nesta fase.
- Decisões humanas registradas em 2026-07-31: owner `caleo-hub`, uso pessoal, sem histórico/telemetria, dois modos no MVP, TXT/SRT selecionáveis e Windows 10.
- O README oficial do Whisper informa VRAM aproximada por modelo (1 GB em `tiny/base` até 10 GB em `large`), mas não publica mínimo formal de CPU/RAM.

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
- **Hipótese:** o perfil padrão é proporcional ao risco.
- **Decisão:** o uso inicial é pessoal.
- **Decisão:** não haverá histórico persistente ou telemetria.
- **Desconhecido:** idiomas, timestamps, locutores e métricas de qualidade.
- **Desconhecido:** mínimo de CPU/RAM e desempenho aceitável do modo local; a fonte oficial só quantifica VRAM.
- **Ambiguidade bloqueadora:** o modo OpenAI exige enviar áudio, mas a resposta sobre conteúdos enviados foi “não”.

## Decisões humanas pendentes

1. Confirmar que, ao escolher o modo OpenAI, o usuário autoriza enviar somente o áudio selecionado para transcrição.
2. Aceitar ou corrigir o perfil de adoção padrão.

## Riscos e bloqueios

- Segredo persistente e repositório público.
- Possível envio de conteúdo sensível a serviço externo.
- Custo de API e consumo local imprevisíveis sem limites.
- Dependências nativas e distribuição de binário ainda não avaliadas.

## Próxima ação recomendada

O responsável humano resolve as duas confirmações restantes. Com o gate da Fase 0 aceito, iniciar a Fase 1 com visão e resultados mensuráveis; não gerar scaffold ou código de produto antes disso.
