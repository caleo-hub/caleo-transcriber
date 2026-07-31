# Threat model — mídia longa e lote

- **Status:** proposto; risco residual pendente no `GATE-SEC-002`
- **Data:** 2026-07-31
- **Complementa:** `docs/security/threat-model.md`

| ID | Ameaça | Controle proposto | Evidência exigida | Residual |
|---|---|---|---|---|
| T2-01 | chunk exceder limite e causar falha/custo inútil | teto interno 24 MB, validação pós-extração antes de upload | testes na borda e spy de requests | limite externo pode mudar |
| T2-02 | retry duplicar cobrança | upload sequencial; estado `ambiguous`; confirmação humana | crash/timeout durante upload | request anterior pode ter concluído |
| T2-03 | checkpoint virar histórico de conteúdo | manifesto sem caminho/texto; resultado DPAPI; TTL 7 dias | schema, canários e teste de expiração | mesma conta/malware acessa DPAPI |
| T2-04 | áudio abandonado após crash | áudio não integra checkpoint; cleanup no startup | kill injetado e inspeção do workspace | janela até próxima abertura |
| T2-05 | misturar resultado de fonte alterada | fingerprint + hash de parâmetros/schema/integridade | testes de adulteração | colisão criptográfica improvável |
| T2-06 | path traversal por referência do manifesto | nome relativo fechado pelo schema e resolução confinada | corpus adversarial | falha futura do parser |
| T2-07 | paralelismo ampliar custo/rate limit | um upload e um item ativos | contador de concorrência | usuário pode iniciar outro app |
| T2-08 | falha apagar sucessos do lote | isolamento por item e saída atômica | falha injetada em cada posição | falha física de disco |
| T2-09 | conteúdo entrar em eventos/logs da fila | eventos por ID/estado/contagem, mensagens próprias | canários e captura de logs | crash dump externo |
| T2-10 | deduplicação remover fala legítima | atuação apenas no overlap e mínimo de três tokens | golden de repetição legítima | timestamps do provider são aproximados |

Nenhum controle autoriza chave real, mídia pessoal, chamada paga ou persistência de fila em teste.
