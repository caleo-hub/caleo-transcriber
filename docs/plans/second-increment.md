# Segundo incremento — mídia longa e lote

- **Status:** aprovado; implementação liberada pelos gates SEC/UX
- **Features:** FEAT-002 e FEAT-003
- **Meta:** uma mudança revisável por tarefa, sem chamada paga

```mermaid
flowchart LR
  T11["TASK-011 Specs, contratos e oráculos"] --> GS["GATE-SEC-002"]
  T11 --> GU["GATE-UX-002"]
  GS --> T12["TASK-012 Planner e recomposição"]
  GS --> T13["TASK-013 Checkpoint DPAPI"]
  T12 --> T14["TASK-014 Extração por chunks"]
  T12 --> T15["TASK-015 TXT e SRT"]
  T13 --> T16["TASK-016 Orquestração longa e retomada"]
  T14 --> T16
  T15 --> T16
  T16 --> T17["TASK-017 Fila sequencial"]
  GU --> T18["TASK-018 UI de lote"]
  T17 --> T18
  T18 --> T19["TASK-019 Aceitação e pacote"]
```

| Ordem | Tarefa | Resultado observável | Gate |
|---:|---|---|---|
| 11 | TASK-011 | specs/ADRs/schemas/vetores aprováveis | SEC e UX antes de código |
| 12 | TASK-012 | plano e merge puros passam nos goldens | segurança aprovada |
| 13 | TASK-013 | checkpoint cifrado, íntegro e expirável | segurança aprovada |
| 14 | TASK-014 | FFmpeg extrai chunks abaixo do limite | segurança aprovada |
| 15 | TASK-015 | writers TXT/SRT atômicos | segurança aprovada |
| 16 | TASK-016 | arquivo longo retoma e recompõe | segurança aprovada |
| 17 | TASK-017 | fila FIFO isolada, um ativo | segurança aprovada |
| 18 | TASK-018 | tabela/ações acessíveis e responsivas | UX aprovada |
| 19 | TASK-019 | gauntlet, screenshots e candidato | novo aceite UX antes de release |

## Estratégia de testes antes do código

TASK-011 versiona schemas, exemplos e vetores; os testes verificam completude, privacidade e
consistência desses oráculos. Cada tarefa seguinte começa conectando o oráculo à unidade pública
correspondente e só então implementa. Alterar um vetor exige mudança de requisito justificada.

## Limites operacionais

- todos os PRs rodam sem rede, chave e mídia pessoal;
- nenhuma dependência nova está autorizada; DPAPI usa APIs do Windows por adapter;
- testes FFmpeg geram mídia sintética curta e simulam duração/tamanho quando possível;
- publicação, instalação e chamada real continuam gates independentes.
