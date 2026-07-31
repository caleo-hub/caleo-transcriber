# Estado da adoção

## Fase atual

Fase 0 — abrir a iniciativa sem abrir o editor de código.

## Resultado esperado desta fase

Ter owner humano, problema inicial compreensível, perfil de risco aceito, contextos `BOOK_ROOT`/`PROJECT_ROOT` e limites de permissão explícitos.

## Estado do gate

**NÃO ATENDIDO.** Há uma proposta coerente, mas owners, contexto de distribuição, política de dados e recorte do MVP ainda precisam de decisão humana.

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
- Repositório remoto `caleo-hub/caleo-transcriber` observado como público, vazio e com branch padrão `main`.
- Perfil padrão proposto e riscos iniciais registrados antes de qualquer escolha tecnológica.
- Matriz de permissões impede código, secrets, chamadas pagas e envio de mídia nesta fase.

## Fatos observados

- O produto alvo é um executável Windows com interface gráfica.
- Há dois modos desejados: OpenAI API e Whisper local.
- Há necessidade de lote, intervalo, destino de saída e progresso.
- A credencial deve ser configurada uma vez.

## Inferências, hipóteses e desconhecidos

- **Inferência:** o usuário primário não deve precisar de terminal.
- **Hipótese:** o perfil padrão é proporcional ao risco.
- **Desconhecido:** público-alvo e forma de distribuição.
- **Desconhecido:** política de dados, retenção, histórico e telemetria.
- **Desconhecido:** formatos, idiomas, timestamps, locutores e métricas de qualidade.
- **Desconhecido:** Windows mínimo e hardware suportado para o modo local.

## Decisões humanas pendentes

1. Aceite dos papéis de product owner e responsável técnico.
2. Uso pessoal, interno, comercial ou distribuição pública.
3. Política de envio, retenção, histórico, logs e telemetria.
4. Um ou dois mecanismos de transcrição no primeiro MVP.
5. Formatos, idiomas e metadados essenciais da transcrição.
6. Windows e hardware mínimos suportados.

## Riscos e bloqueios

- Segredo persistente e repositório público.
- Possível envio de conteúdo sensível a serviço externo.
- Custo de API e consumo local imprevisíveis sem limites.
- Dependências nativas e distribuição de binário ainda não avaliadas.

## Próxima ação recomendada

O responsável humano revisa o brief e responde às seis decisões. Com o gate da Fase 0 aceito, iniciar a Fase 1 com visão e resultados mensuráveis; não gerar scaffold ou código de produto antes disso.
