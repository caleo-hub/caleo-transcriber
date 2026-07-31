# ADR-0007 — Fila FIFO sequencial e efêmera

- **Status:** aceito
- **Data:** 2026-07-31
- **Decisor:** `caleo-hub`

## Contexto

O lote precisa preservar sucessos, continuar após falha, cancelar itens e repetir somente falhas.
Paralelismo entre arquivos aumentaria custo, pressão sobre FFmpeg e complexidade de UX.

## Decisão proposta

Criar um agregado de domínio `BatchQueue`, independente de PySide6, com ordem FIFO e um scheduler de
aplicação que inicia no máximo um item. A fila e suas tentativas vivem somente em memória.

- itens duplicados são identificados pela identidade da fonte e não entram duas vezes;
- configurações comuns ficam imutáveis enquanto a execução está ativa;
- terminar o ativo em qualquer estado terminal libera o próximo `queued`;
- cancelamento pendente é síncrono e sem efeitos externos;
- cancelamento ativo sinaliza o token existente;
- `retry_failed()` cria novas tentativas apenas para falhas, preservando ordem e sucessos;
- progresso global é contagem de terminais e resumo por estado;
- eventos carregam IDs efêmeros e estados, nunca caminhos ou conteúdo.

## Consequências

- comportamento de fila é testável sem thread/UI;
- throughput pode ser menor, mas custo e recursos são previsíveis;
- FEAT-002 pode paralelizar internamente no futuro sem alterar o contrato de um item ativo;
- fechar o aplicativo descarta a fila, mantendo apenas checkpoints técnicos cifrados da FEAT-002.

## Alternativas rejeitadas

- `ThreadPoolExecutor` por arquivo: viola o default aprovado de um item ativo;
- interromper lote na primeira falha: viola isolamento por item;
- persistir a fila: criaria histórico não autorizado;
- percentual global ponderado por duração: pareceria precisão temporal sem base real.

## Rollback

Reverter scheduler/agregado e retornar à jornada de arquivo único; saídas concluídas e credenciais
permanecem intocadas.
