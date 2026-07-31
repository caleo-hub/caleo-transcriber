# Plano de testes — primeira fatia

- **Status:** aprovado como sistema de verificação da Fase 6
- **Data:** 2026-07-31
- **Fontes:** FEAT-001, constituição, arquitetura, contrato do provider e threat model

## Princípio

Nenhum teste isolado prova correção. O gauntlet combina verificações rápidas, contratos, propriedades, integração controlada, aceitação, segurança e validação manual. Cobertura numérica é diagnóstico, não gate substituto de requisitos.

## Matriz requisito/risco → evidência

| Fonte | Pergunta | Verificação | Quando | Estado |
|---|---|---|---|---|
| CA-001 | MP3/WAV gera TXT pela OpenAI? | componente com provider fake + integração real separada e aprovada | PR / manual | planejado com implementação |
| CA-002, T-02 | MP4 envia somente áudio? | spy multipart + probe do arquivo preparado | PR | critério protegido; teste na implementação do adapter |
| CA-003, T-04 | arquivo existente permanece intacto? | integração filesystem + disputa de nome | PR | planejado |
| CA-004 | entrada inválida não chama provider? | tabela negativa com spy provider | PR | planejado |
| CA-005 | erros externos viram categorias estáveis? | contrato parametrizado 401/403/429/timeout/5xx | PR | schema ativo; mapper planejado |
| CA-006 | cancelamento limpa temporários e não conclui? | teste por fronteira de etapa + estado | PR | máquina de estados ativa; componente planejado |
| CA-007 | progresso é honesto? | teste do view model sem total conhecido | PR | planejado |
| CA-008 | reinício não mostra histórico? | E2E reinicia app com storage inspecionado | release | planejado |
| CA-009, T-01/T-10 | logs não contêm segredo/conteúdo? | canários + captura de logs + gitleaks | PR | gitleaks ativo; teste de runtime planejado |
| CA-010 | Windows 10 x64 e teclado funcionam? | smoke em VM + checklist manual de acessibilidade | release | workflow Windows parcial; VM planejada |
| distribuição | download do GitHub instala e abre sem runtime externo? | build limpo, instalação/desinstalação e smoke em VM Windows 10 x64 | release | planejado para Fases 9/entrega |
| contrato v1 | success/failure permanecem compatíveis? | JSON Schema + exemplos aprovados | PR | ativo |
| arquitetura | core não importa infraestrutura? | Import Linter | PR | ativo |
| supply chain, T-08 | dependências conhecidas e build íntegro? | pins, Dependabot, pip-audit, build | PR | ativo |
| segredo | mídia, `.env` ou chave entram no repo? | git policy + gitleaks | PR | ativo |

## Camadas e limites

- **format/lint/tipos:** eliminam inconsistência mecânica; não comprovam comportamento;
- **unitário/propriedade:** invariantes e máquina de estados; não comprovam integração externa;
- **contrato:** schemas e mapeamento do provider; não comprova semântica da OpenAI;
- **componente:** caso de uso com fakes e filesystem temporário; não comprova pacote Windows;
- **integração:** FFmpeg, Credential Manager e adapter HTTP controlado; sem API paga no CI;
- **aceitação/E2E:** jornada observável e pacote Windows; seletivos;
- **segurança:** secrets, dependências, logs e entradas adversariais; não prova ausência de zero-day;
- **manual:** acessibilidade, UX, Windows 10 e chamada real aprovada.

## Independência dos oráculos

1. Critérios e exemplos foram aprovados pelo owner antes do código.
2. Specs, contratos, `tests/acceptance/` e segurança possuem CODEOWNERS do owner.
3. Implementação não pode alterar teste/oráculo para fazê-lo passar sem explicar a mudança de requisito.
4. CI executa os comandos em máquina separada.
5. Chamada real à OpenAI, teste em VM e aceite de UX exigem execução/revisão humana.
6. Para mudanças moderadas/altas, revisão humana verifica cenários, não apenas o verde do CI.

## Dados de teste

- gerar mídia sintética curta e determinística em script versionado;
- nunca versionar mídia pessoal;
- golden files contêm somente fala sintética conhecida;
- falhas de API são respostas simuladas, sem chave;
- limites usam arquivos esparsos/metadados quando possível, evitando fixtures grandes.

## Checks bloqueadores

`verify` e `secret scan` devem ser required checks na proteção de `main`. Vulnerabilidade conhecida relevante, contrato quebrado, teste falho, import proibido, secret detectado ou build inválido bloqueiam merge. A configuração do ruleset no GitHub é uma ação administrativa humana; sua ausência impede declarar branch protection comprovada.

## Testes fora do CI padrão

- OpenAI real: somente após aprovação de custo/dados, com chave no Credential Manager e áudio sintético;
- VM Windows 10 x64, acessibilidade e antivírus: antes da release;
- instalar o `.exe` obtido do próprio GitHub Release em VM limpa e abrir pelo menu Iniciar;
- benchmark, mutation/fuzz focal e SBOM: antes de ampliar autonomia ou empacotar release.

## Evidência de conclusão

- `verify.cmd`: format, lint, mypy, Import Linter, pytest, build e pip check;
- `audit.cmd`: pip-audit e secret scan local;
- CI Windows e gitleaks configurados;
- matriz acima rastreia cada CA e ameaça material.

## Extensão proposta — segundo incremento

| Fonte | Pergunta | Verificação | Gate |
|---|---|---|---|
| LM-CA-001/002, T2-01 | todo upload respeita tipo e 24 MB? | planner + extração real curta + spy | SEC |
| LM-CA-003–005, T2-10 | fronteira/timeline/dedup preservam fala? | propriedades e goldens versionados | SEC |
| LM-CA-006 | TXT/SRT são válidos e equivalentes? | parser independente e golden Unicode | SEC |
| LM-CA-007–010, T2-02–06 | retomada evita custo e vazamento? | crash por estado, schema, DPAPI, adulteração e TTL | SEC |
| LM-CA-011/012 | cancelar/progresso são honestos? | componente com token e eventos | SEC/UX |
| BATCH-CA-001–007 | fila isola, cancela e repete corretamente? | máquina de estados + falha em cada posição | SEC |
| BATCH-CA-008–010 | tabela é compreensível, acessível e efêmera? | pytest-qt, screenshot e reinício | UX |
| BATCH-CA-011–016 | seleção, limpeza, ordem, pausa e cancelamento preservam dados? | domínio + scheduler + pytest-qt + screenshot | UX/SEC |

TASK-011 valida os oráculos sem importar `src`. Depois dos gates, cada teste comportamental é
conectado à API pública antes da implementação correspondente.
