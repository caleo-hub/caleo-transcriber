# Estratégia de referência — áudio e vídeo longos

- **Status:** candidata para ratificação na arquitetura
- **Owner:** `caleo-hub`
- **Data:** 2026-07-31
- **Escopo:** comportamento interno; nenhuma configuração de chunk é exposta ao usuário

## Resumo

A estratégia adotada como referência é **segmentação adaptativa com continuidade e recomposição determinística**, não corte fixo por duração.

O aplicativo extrai somente o áudio selecionado, escolhe o caminho adequado ao provedor, limita concorrência conforme recursos, salva checkpoints temporários por unidade e recompõe uma única transcrição na timeline do arquivo original.

## O que as referências oficiais estabelecem

### OpenAI API

A documentação oficial de transcrição de arquivos informa:

- arquivos enviados à Transcriptions API podem ter até 25 MB;
- para gravações maiores, deve-se comprimir ou dividir em partes de até 25 MB;
- deve-se evitar corte no meio de uma sentença, pois a perda de contexto reduz a precisão;
- o contexto do chunk anterior pode ser fornecido por prompt para gravações longas.

Fonte: [OpenAI — File transcription](https://developers.openai.com/api/docs/guides/speech-to-text#longer-inputs).

### Whisper local

O `transcribe()` oficial lê o arquivo completo e processa o áudio internamente com uma janela deslizante de 30 segundos. Portanto, 30 segundos é uma característica interna do modelo, não um tamanho de arquivo que a interface deva pedir ao usuário.

Fonte: [OpenAI Whisper — README](https://github.com/openai/whisper/blob/main/README.md#python-usage).

## Estratégia adaptada ao Caleo Transcriber

### 1. Analisar e preparar

1. Detectar duração, streams, codec, tamanho e trecho solicitado.
2. Extrair somente o áudio necessário para um temporário controlado.
3. Normalizar para um formato adequado ao mecanismo, sem alterar a timeline lógica.
4. Construir um plano automático por item e exibir apenas etapas compreensíveis ao usuário.

### 2. Caminho OpenAI

1. Se o áudio preparado estiver abaixo do limite com margem de segurança, enviar em uma única requisição.
2. Se exceder o limite, criar chunks por **tamanho estimado**, procurando silêncio/pausa perto da fronteira e nunca usando 30 minutos como corte fixo.
3. Manter pequena região de overlap para não perder palavras na borda; a duração exata será definida por benchmark.
4. Quando o fluxo for sequencial e o modelo suportar, usar contexto final do chunk anterior como prompt do seguinte.
5. Repetir somente chunks com falha, aplicando backoff e respeitando rate limit e custo.

O alvo candidato é manter cada upload abaixo de 25 MB com margem operacional; o valor exato da margem pertence à arquitetura/configuração interna.

### 3. Caminho Whisper local

1. Preferir o `transcribe()` de arquivo completo, que já usa janelas internas de 30 segundos.
2. Adicionar segmentação externa somente se benchmarks demonstrarem benefício para cancelamento, retomada, memória ou progresso.
3. Em uma única GPU, começar com um worker de inferência; paralelismo só aumenta após prova de ganho sem falta de memória.
4. Em CPU, dimensionar workers por benchmark e manter reserva para a interface continuar responsiva.

### 4. Política de paralelismo automático

Prioridade de paralelismo:

1. preparação de mídia sem competir com inferência crítica;
2. chunks do item ativo somente quando houver fronteiras independentes ou recomposição robusta;
3. arquivos diferentes da fila ficam sequenciais no MVP, conforme o default de um item ativo.

O scheduler deve reduzir concorrência automaticamente diante de memória baixa, GPU ocupada, throttling, rate limit ou custo projetado. O usuário vê fila e progresso, não número de workers.

### 5. Checkpoints, retomada e cancelamento

- Cada chunk recebe ID, intervalo global, hash da fonte/parâmetros, estado, tentativas e resultado temporário.
- Um manifesto temporário permite repetir somente a parte que falhou ou retomar após interrupção.
- Cancelar impede novos chunks, solicita cancelamento do ativo quando possível e preserva consistência.
- Após saída consolidada, manifesto, áudio e resultados parciais são removidos.
- Esses dados técnicos não formam histórico de usuário.

### 6. Recomposição

1. Converter timestamps locais em offsets da mídia original, incluindo o início de um segmento escolhido.
2. Ordenar resultados pelo intervalo global.
3. Resolver overlap por timestamps e similaridade textual, removendo duplicações sem apagar fala legítima.
4. Detectar lacuna, inversão ou sobreposição inválida antes de salvar.
5. Gerar TXT pela sequência consolidada e SRT por cues válidos na timeline original.
6. Escrever saída de forma atômica e aplicar a política de nome sem sobrescrita.

## Por que não paralelizar tudo

Paralelismo irrestrito pode aumentar custo, atingir rate limits, esgotar VRAM/RAM e piorar continuidade entre chunks. A referência para o MVP é concorrência **limitada e adaptativa**. Ganho de desempenho só é aceito quando benchmarks e testes de fronteira mantêm a qualidade.

## Antipadrões rejeitados

- cortar sempre a cada 30 minutos;
- cortar no meio de fala quando há pausa próxima;
- concatenar textos sem offsets e deduplicação;
- iniciar todos os chunks ao mesmo tempo;
- repetir o arquivo inteiro quando somente um chunk falha;
- expor bitrate, overlap, chunk size ou workers como configuração obrigatória;
- enviar o vídeo completo quando somente o áudio/segmento é necessário.

## Decisões reservadas para arquitetura e benchmark

- codec, bitrate e margem abaixo de 25 MB;
- detector de silêncio e tolerância de fronteira;
- duração de overlap;
- algoritmo de deduplicação;
- número máximo de workers por CPU, GPU e API;
- tamanho do contexto passado entre chunks;
- formato e proteção do manifesto temporário.

## Testes obrigatórios da estratégia

- 29:59, 30:00 e 30:01 de duração;
- arquivo abaixo, exatamente na borda operacional e acima do limite de upload;
- fala contínua na fronteira e silêncio próximo à fronteira;
- palavra repetida legítima versus duplicação causada por overlap;
- timestamps com segmento iniciado longe de zero;
- falha, retry, cancelamento e retomada em chunk intermediário;
- memória insuficiente, rate limit e redução automática de concorrência;
- equivalência aceitável entre execução inteira e segmentada;
- TXT e SRT sem lacunas, inversões ou cues inválidos.

## Gate

Esta referência restringe a futura arquitetura, mas não escolhe biblioteca de chunking, valores numéricos ou scheduler. Ela será aprovada junto da constituição e ratificada por ADR e benchmarks na Fase 4.
