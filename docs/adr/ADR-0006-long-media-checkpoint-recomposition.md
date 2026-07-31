# ADR-0006 — Segmentação, recomposição e checkpoint de mídia longa

- **Status:** proposto; depende de `GATE-SEC-002`
- **Data:** 2026-07-31
- **Decisor:** `caleo-hub`

## Contexto

A OpenAI limita uploads de transcrição, falhas intermediárias podem gerar custo repetido e a
recomposição precisa preservar fala e timestamps. A aplicação não mantém histórico, mas precisa
retomar trabalho interrompido sem reenviar partes confirmadas.

## Decisão proposta

### Plano e execução

- retirar o teto funcional de 30 minutos;
- manter MP3 mono a 64 kbps;
- upload máximo interno de 24.000.000 bytes e alvo de chunk de 20.000.000 bytes;
- estimar fronteiras por proporção bytes/duração, buscar silêncio a ±15 segundos e aplicar overlap
  de dois segundos;
- validar o tamanho de cada arquivo extraído e reduzir a fronteira antes de enviá-lo se necessário;
- executar chunks sequencialmente no primeiro incremento.

### Recomposição

Segmentos do provider recebem o offset global do chunk. A função pura de recomposição ordena,
valida intervalos e limita deduplicação à janela de overlap. Segmento totalmente coberto é
descartado; em cobertura parcial, remove-se apenas o maior sufixo/prefixo normalizado de pelo menos
três tokens. Repetição fora da janela permanece. TXT e SRT usam o mesmo resultado consolidado.

### Checkpoint

O core conhece uma porta `CheckpointStore`; a implementação Windows usa `%LOCALAPPDATA%` e DPAPI
com escopo do usuário atual. O manifesto JSON versionado e atômico contém apenas:

- ID aleatório, fingerprint da fonte e hash de parâmetros;
- intervalos, estado, tentativas e referência relativa do resultado;
- versão do schema, integridade e expiração.

Não contém caminho completo nem texto. Cada resultado de chunk é protegido separadamente. O
fingerprint combina tamanho, `mtime_ns` e SHA-256 de blocos do início/fim; ele detecta troca sem
obrigar hash integral do arquivo.

O estado segue `pending → uploading → confirmed|failed`. Repetição manual muda `failed → pending`.
Reinício em `uploading` produz `ambiguous` e exige confirmação humana antes de novo envio. Resultado
só vira `confirmed` após validação e persistência atômica. Áudio de chunk nunca é checkpoint: é
removido após o request e reextraído quando preciso.

Checkpoints expiram em sete dias. Sucesso, cancelamento explícito, incompatibilidade ou expiração
remove manifesto/resultados; startup remove áudio abandonado antes de oferecer retomada.

## Consequências

- maior número de requests que uma compactação extrema, com limite e custo mais previsíveis;
- retomada reduz repetição de custo, mas mantém texto cifrado por prazo limitado;
- DPAPI protege contra outras contas/offline, não contra malware na mesma conta;
- execução sequencial prioriza continuidade, previsibilidade e rate limit sobre velocidade;
- paralelismo futuro exige benchmark de qualidade/custo e nova decisão.

## Alternativas rejeitadas

- corte fixo aos 30 minutos: não representa o limite real;
- chunks sem overlap: pode perder palavras;
- concatenação textual simples: duplica bordas e perde timeline;
- resultados parciais em texto claro: conflita com privacidade e ausência de histórico;
- retry automático de upload ambíguo: pode cobrar duas vezes;
- vários uploads simultâneos: aumenta rate limit/custo e complica contexto/retomada.

## Rollback

Remover planner/checkpoint e restaurar o limite anterior de 30 minutos. O cleanup da versão de
rollback deve reconhecer e eliminar workspaces do schema v1 sem tentar descriptografar conteúdo
para logs.
