# FEAT-002 — Transcrever mídia longa automaticamente

- **Status:** proposta; gate de segurança pendente
- **Owner:** `caleo-hub`
- **Risco:** alto nas fronteiras de custo, retenção temporária e recomposição
- **Referência:** [`docs/product/long-media-strategy.md`](../../docs/product/long-media-strategy.md)

## Intenção

Aceitar áudio ou vídeo acima de 30 minutos sem configuração de divisão, enviar somente áudio em
partes abaixo do limite operacional da OpenAI, preservar a timeline e produzir um único TXT ou SRT
sem lacunas ou duplicações introduzidas pelo processamento.

## Escopo

- MP4, MP3 e WAV, arquivo inteiro;
- `whisper-1`, com chunks sequenciais no primeiro incremento;
- divisão governada por bytes e pausas próximas, não por um corte fixo de 30 minutos;
- overlap interno de dois segundos;
- timestamps globais, deduplicação determinística e saída TXT ou SRT;
- checkpoint por chunk, retomada após falha/encerramento e limpeza de temporários;
- nenhuma configuração de tamanho, overlap, bitrate ou concorrência na UI.

Não entra: seleção de trecho, Whisper local, diarização, edição da transcrição, paralelismo entre
uploads ou promessa de duração ilimitada. O limite prático depende de mídia legível e espaço local.

## Regras

1. Duração maior que 30 minutos não é erro.
2. Áudio preparado abaixo de `24_000_000` bytes usa uma requisição, mesmo acima de 30 minutos.
3. Áudio maior é dividido com alvo de `20_000_000` bytes; cada resultado precisa permanecer
   estritamente abaixo de `24_000_000` bytes ou ser reduzido antes de qualquer envio.
4. A fronteira procura silêncio em até 15 segundos para cada lado do ponto estimado; sem silêncio,
   usa o ponto estimado e overlap de dois segundos.
5. Chunks são enviados em ordem e somente um upload fica ativo. Paralelismo exige benchmark e ADR
   posterior.
6. Cada request usa nome neutro e contém somente o MP3 do intervalo planejado.
7. Timestamps locais recebem o início global do chunk; o início de um eventual trecho futuro também
   integrará esse offset.
8. Deduplicação só atua dentro do overlap: primeiro por intervalo temporal e, em empate parcial,
   pelo maior sufixo/prefixo normalizado de ao menos três tokens. Repetição fora do overlap é fala
   legítima e permanece.
9. TXT e SRT derivam da mesma sequência consolidada e nunca disparam nova transcrição.
10. SRT possui cues crescentes, `start < end`, sem sobreposição e na timeline do arquivo original.
11. Checkpoint confirmado evita reenviar chunks já concluídos. Falha conhecida permanece `failed`
    até repetição explícita do item, quando volta a `pending`.
12. Upload interrompido em estado ambíguo nunca é repetido automaticamente, para não duplicar custo;
    a UI exige confirmação explícita.
13. Manifesto não contém caminho completo nem texto. Resultados parciais persistentes ficam
    protegidos por DPAPI do usuário atual e expiram em sete dias.
14. Áudio temporário é removido após cada request e na recuperação do próximo início. Ele é
    reextraído quando necessário.
15. Sucesso ou cancelamento explícito remove todo o checkpoint; falha recuperável preserva apenas o
    mínimo necessário à retomada.
16. Manifesto e resultado cujo fingerprint, parâmetros, schema ou integridade não coincidam são
    ignorados e removidos; nunca são misturados com a nova execução.

## Fluxo principal

1. Analisar fonte e espaço necessário.
2. Preparar áudio mono MP3 a 64 kbps.
3. Se o tamanho exceder o limite operacional, criar plano por bytes e ajustar fronteiras em pausas.
4. Para cada chunk pendente: extrair, marcar envio, transcrever, validar, proteger o resultado,
   confirmar o checkpoint e remover o áudio daquele chunk.
5. Converter segmentos para a timeline global e recompor.
6. Validar a sequência final e gravar TXT ou SRT atomicamente, sem sobrescrever.
7. Remover checkpoint e temporários; mostrar a saída única.

## Retomada

Ao selecionar novamente a mesma fonte e os mesmos parâmetros, a aplicação compara fingerprint e
oferece continuar. Chunks confirmados são reutilizados; falhos voltam a pendentes somente após a
ação de repetir; chunk ambíguo exige confirmação para novo envio. A fila não reaparece como
histórico após reinício.

## Critérios de aceitação

### LM-CA-001 — Limite é por bytes

29:59, 30:00 e 30:01 são aceitos. Uma mídia acima de 30 minutos abaixo de 24 MB usa um request; uma
mídia menor que 30 minutos acima do limite é segmentada.

### LM-CA-002 — Uploads seguros

Todo request contém MP3 de áudio, nome neutro e menos de 24 MB; nenhum contêiner de vídeo é enviado.

### LM-CA-003 — Fronteira de fala

Havendo silêncio dentro da janela de busca, a fronteira o utiliza. Sem silêncio, o plano mantém
continuidade com overlap de dois segundos.

### LM-CA-004 — Timeline global

Os segmentos finais ficam ordenados e recebem offsets globais corretos, inclusive quando o chunk
começa longe de zero.

### LM-CA-005 — Deduplicação conservadora

Texto repetido pelo overlap aparece uma vez; palavra ou frase repetida fora do overlap permanece.

### LM-CA-006 — TXT e SRT

O formato escolhido produz um arquivo consolidado. O SRT passa em parser independente e possui
cues crescentes, válidos e não sobrepostos.

### LM-CA-007 — Falha isolada e retomada

Falha no chunk intermediário não perde chunks confirmados. Nova tentativa envia somente chunks
pendentes, depois recompõe a mesma saída esperada.

### LM-CA-008 — Estado ambíguo

Encerramento ou timeout durante upload marca o chunk como ambíguo e não gera retry automático.

### LM-CA-009 — Integridade da retomada

Alterar fonte, parâmetros, schema ou resultado protegido invalida o checkpoint e impede mistura.

### LM-CA-010 — Cleanup e retenção

Sucesso/cancelamento removem o workspace. Na abertura seguinte, áudio abandonado e checkpoints
expirados são removidos. Falha recuperável mantém somente manifesto e resultados protegidos.

### LM-CA-011 — Cancelamento

Cancelar impede novos uploads, solicita cancelamento do ativo e nunca publica saída parcial como
final.

### LM-CA-012 — Progresso honesto

A UI mostra quantidade de chunks confirmados e etapa ativa; não converte tempo desconhecido em
percentual inventado.

## Exemplos e contraexemplos

Os vetores canônicos ficam em `contracts/examples/long-media-cases.json`. São contraexemplos:
reenviar chunk confirmado, concatenar textos sem timestamps, remover repetição fora do overlap,
manter áudio após sucesso, salvar texto claro em manifesto ou repetir upload ambíguo sozinho.

## Gate

Implementação bloqueada até aprovação de `GATE-SEC-002`: limites, retenção por sete dias, DPAPI,
estado ambíguo e concorrência cloud igual a um.
