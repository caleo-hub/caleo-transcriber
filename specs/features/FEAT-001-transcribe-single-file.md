# FEAT-001 — Transcrever um arquivo inteiro em TXT

- **Status:** em clarificação
- **PRD relacionado:** [`docs/product/prd.md`](../../docs/product/prd.md)
- **Constituição:** [`specs/constitution.md`](../constitution.md)
- **Owner:** `caleo-hub`
- **Risco:** moderado; elevado nas fronteiras de segredo e envio externo

## Intenção

Permitir que o usuário escolha um arquivo de áudio ou vídeo de até 30 minutos, use um provedor já configurado e obtenha uma transcrição TXT no diretório escolhido, com estado compreensível, cancelamento seguro e nenhuma sobrescrita ou histórico persistente.

Esta é a menor fatia ponta a ponta proposta para validar seleção, preparação de mídia, fronteira de provedor, progresso e escrita de saída.

## Escopo

- um arquivo por trabalho;
- arquivo inteiro, sem seleção de segmento;
- duração detectada entre mais de zero e 30 minutos inclusive;
- formatos iniciais propostos: MP4, MP3 e WAV;
- transcrição pela API da OpenAI com o modelo `whisper-1` já configurado;
- em entradas de vídeo, extração e envio somente da faixa de áudio;
- saída TXT no diretório escolhido;
- etapas e estado do trabalho;
- cancelamento de melhor esforço e repetição após falha;
- nome de saída seguro sem sobrescrita;
- limpeza de temporários e ausência de histórico.

## Fora de escopo

- configuração, teste ou remoção da chave da OpenAI;
- download e gestão de modelos locais;
- transcrição com Whisper local, que será um adaptador opcional em incremento posterior;
- arquivos múltiplos e fila em lote;
- seleção de segmento;
- saída SRT;
- arquivos acima de 30 minutos e chunking externo;
- paralelismo;
- identificação de locutores, tradução ou edição;
- release/instalador final.

As capacidades acima continuam no MVP e receberão specs próprias.

## Atores e permissões

- **Usuário:** seleciona arquivo, destino e inicia/cancela/repete.
- **Aplicação:** pode ler somente a fonte escolhida, criar temporários controlados e gravar no destino escolhido.
- **OpenAI:** recebe somente o áudio preparado quando esse modo for explicitamente selecionado.

## Pré-condições

1. Windows 10 x64.
2. OpenAI está selecionada, com credencial válida já protegida.
3. Arquivo existe, é legível, tem formato suportado e duração detectável de até 30 minutos.
4. Diretório de saída existe ou pode ser criado pela aplicação e é gravável.
5. Há espaço temporário e de saída suficiente, ou a aplicação consegue detectar a insuficiência antes da transcrição.

## Máquina de estados

```text
pronto -> preparando -> transcrevendo -> salvando -> concluído
                   \-> falhou ---------> repetir
                   \-> cancelando -----> cancelado
```

Transições fora desse grafo são inválidas. `concluído`, `falhou` e `cancelado` são terminais para a tentativa atual.

## Fluxo principal

1. O usuário adiciona um arquivo suportado.
2. A aplicação detecta tipo, duração e legibilidade.
3. A interface mostra que o modo OpenAI (cloud) enviará áudio e poderá gerar custo.
4. O usuário escolhe o diretório de saída.
5. A interface apresenta arquivo, duração, provedor, formato TXT e destino antes do início.
6. O usuário inicia a transcrição.
7. A aplicação extrai/prepara somente o áudio necessário em temporário controlado, inclusive para MP4.
8. O adaptador OpenAI envia o áudio ao endpoint de transcrição com `whisper-1` e recebe o texto.
9. A aplicação normaliza o texto sem inventar ou resumir conteúdo.
10. A saída é gravada atomicamente no nome resolvido.
11. Temporários são removidos.
12. A interface mostra conclusão e o caminho do arquivo criado.

## Fluxos alternativos

### A1 — OpenAI

- O modo cloud permanece visível antes e durante o envio.
- Somente o áudio extraído é enviado; o vídeo original não é transmitido.
- Cancelamento após envio não promete revogar dados já transmitidos; impede etapas seguintes quando possível.

### A3 — Colisão de nome

- Nome primário: `<nome-base>.txt`.
- Se existir, tentar `<nome-base> (1).txt`, depois incrementar até encontrar nome livre.
- A resolução e a criação devem evitar sobrescrita mesmo se outro processo criar o mesmo nome simultaneamente.

### A4 — Repetir falha

- A repetição cria nova tentativa para o mesmo arquivo e parâmetros visíveis.
- Nenhum resultado parcial da tentativa anterior é tratado como saída final.

## Erros e recuperação

| Condição | Comportamento observável | Recuperação |
|---|---|---|
| arquivo inexistente, ilegível ou corrompido | rejeitar antes de iniciar; explicar o motivo conhecido | escolher outro arquivo |
| formato não suportado | listar formatos aceitos | converter fora do app ou escolher outro |
| duração zero ou acima de 30 minutos | impedir esta fatia e explicar o limite | fluxo futuro de mídia longa |
| diretório sem permissão | não transcrever | escolher outro destino |
| disco insuficiente | falhar antes da transcrição quando detectável | liberar espaço e repetir |
| credencial ausente/inválida | não enviar ou interromper; nunca mostrar a chave | abrir configuração e substituir/testar |
| rede, timeout ou rate limit | marcar falha com categoria e ação | repetir manualmente; política automática posterior |
| falha ao salvar | não declarar sucesso; preservar texto apenas durante a tentativa | corrigir destino e repetir/salvar quando especificado |
| cancelamento | parar novas etapas; remover saída incompleta e temporários | iniciar nova tentativa |

## Regras e invariantes

1. Uma tentativa possui exatamente um arquivo, um provedor, um destino e um estado atual.
2. `concluído` implica um TXT final existente e legível.
3. Nenhum outro estado implica existência de saída final nova.
4. Arquivo preexistente nunca é alterado.
5. OpenAI recebe somente áudio derivado da fonte selecionada.
6. O arquivo de vídeo original nunca é enviado; somente o áudio extraído pode sair do computador.
7. Chave, mídia, transcrição e caminhos completos sensíveis não aparecem em logs.
8. Percentual só aparece quando derivado de trabalho mensurável; caso contrário, a etapa é indeterminada.
9. Cancelamento não pode transformar tentativa em `concluído`.
10. Reiniciar o aplicativo não apresenta histórico da tentativa anterior.
11. O texto não é resumido, traduzido ou “corrigido” semanticamente pela aplicação.

## Dados e contratos conceituais

```text
TranscriptionAttempt
  id efêmero
  source path (somente memória/estado efêmero)
  source duration
  provider: openai
  model: whisper-1
  output directory
  output format: txt
  state
  stage
  progress: known(percent) | indeterminate
  error category opcional
```

O contrato técnico, tipos de erro e portas serão definidos na arquitetura. Este modelo não autoriza persistência de histórico.

## Alinhamento com a arquitetura de referência

```text
Interface -> TranscriptionUseCase -> TranscriptionProvider (porta)
                    |                        |
                    v                        v
        MediaSource/AudioExtractor   OpenAIWhisperAdapter
                    |
                    v
              TxtOutputWriter
```

A primeira fatia implementa o caminho completo com OpenAI. O núcleo conhece apenas a porta `TranscriptionProvider`; o Whisper local será acrescentado depois como outro adaptador. Essa ordem entrega funcionamento em qualquer computador Windows 10 x64 com acesso à internet e evita acoplar a experiência principal aos requisitos de hardware do modo local.

O `whisper-1` fica isolado no adaptador. Embora a documentação atual recomende modelos `gpt-transcribe` para transcrição geral nova, `whisper-1` é mantido por decisão do owner e por oferecer granularidade de timestamps necessária à futura saída SRT. A arquitetura permite trocar ou adicionar modelos sem alterar o caso de uso.

## Requisitos não funcionais

- A interface permanece responsiva durante preparação, inferência, rede e escrita.
- O usuário consegue configurar e iniciar o primeiro trabalho em até três minutos, excluindo preparação de provedor e tempo de transcrição.
- Operação principal por teclado, foco visível e estados não dependentes apenas de cor.
- O aplicativo deve sobreviver a falha do worker sem encerrar a janela principal.
- A saída final usa UTF-8 e não fica parcialmente visível.
- O comportamento deve ser testável com provedor substituto, sem chave ou mídia real.

## Segurança e privacidade

- Não solicitar chave ao agente, teste automatizado ou log.
- Usar mídia sintética ou licenciada nas evidências.
- Não enviar nome/caminho do vídeo como metadado desnecessário.
- Remover áudio temporário em sucesso, falha e cancelamento; executar limpeza de recuperação na próxima abertura.
- Mensagem do modo OpenAI precisa tornar a transferência externa evidente.

## Observabilidade local

Sem telemetria. A UI expõe estado, etapa, categoria de erro e ação. Logs técnicos são locais, mínimos, redigidos e desligáveis; não contêm conteúdo. Evidências de teste usam eventos sintéticos e resultados estruturados.

## Critérios de aceitação

### CA-001 — TXT OpenAI

Dado um MP3 ou WAV sintético válido e credencial de teste autorizada, quando o usuário iniciar no modo OpenAI, então somente o áudio deve ser enviado ao `whisper-1` e um TXT deve ser criado após resposta válida.

**Evidência planejada:** teste de contrato com provedor substituto; teste real separado e aprovado.

### CA-002 — Vídeo envia somente áudio

Dado um MP4 válido com faixa de áudio, quando o usuário iniciar a transcrição, então a aplicação deve extrair a faixa de áudio, não enviar o contêiner de vídeo e produzir o mesmo contrato TXT das entradas de áudio.

**Evidência planejada:** teste de integração do extrator e inspeção da requisição no provedor substituto.

### CA-003 — Arquivo preexistente

Dado que `aula.txt` já existe, quando `aula.mp4` concluir, então o arquivo antigo permanece byte a byte igual e o novo resultado usa `aula (1).txt` ou próximo sufixo livre.

**Evidência planejada:** teste de integração de filesystem e concorrência de nome.

### CA-004 — Entrada inválida

Dado arquivo ilegível, corrompido, vazio, acima de 30 minutos ou formato fora desta fatia, quando for selecionado, então a aplicação não inicia provedor e apresenta motivo e ação.

**Evidência planejada:** tabela de testes negativos.

### CA-005 — Falha do provedor

Dado timeout, rate limit, credencial inválida ou falta de memória, quando o provedor falhar, então a tentativa termina `falhou`, nenhuma saída final é criada e a repetição fica disponível.

**Evidência planejada:** falhas injetadas por categoria.

### CA-006 — Cancelamento

Dado trabalho em preparação ou transcrição, quando o usuário cancelar, então o estado passa por `cancelando` para `cancelado`, novas etapas param e saída incompleta/temporários são removidos.

**Evidência planejada:** testes em cada fronteira de etapa.

### CA-007 — Progresso honesto

Dado um provedor sem percentual real, quando estiver processando, então a UI mostra etapa indeterminada e nunca um percentual fabricado.

**Evidência planejada:** teste da máquina de estados da apresentação.

### CA-008 — Sem histórico

Dado trabalho concluído, falho ou cancelado, quando o aplicativo reiniciar, então nenhuma lista de trabalhos anteriores é mostrada.

**Evidência planejada:** teste de reinicialização e inspeção do armazenamento.

### CA-009 — Segredo e conteúdo ausentes

Dado sucesso e todas as falhas previstas, então chave, áudio e texto transcrito não aparecem em logs, mensagens técnicas ou arquivos de configuração legíveis.

**Evidência planejada:** secret scanning e varredura de artefatos/logs.

### CA-010 — Compatibilidade e acessibilidade

Dado Windows 10 x64 limpo, quando o usuário operar por teclado, então consegue selecionar arquivo, provedor e destino, iniciar/cancelar e perceber estados sem depender apenas de cor.

**Evidência planejada:** smoke test em VM e checklist de acessibilidade.

## Exemplos

| Entrada | Provedor | Estado esperado | Saída |
|---|---|---|---|
| `entrevista.wav`, 02:15 | OpenAI pronto | concluído | `entrevista.txt` |
| `aula.mp3`, 29:59 | OpenAI pronto | concluído | `aula.txt` |
| `aula.mp4`, 30:00 | OpenAI pronto | concluído; envia só áudio | `aula.txt` |
| `aula.mp4`, 30:01 | OpenAI pronto | recusado nesta fatia | nenhuma; direcionar para feature longa |
| `silencio.wav`, 01:00 | OpenAI pronto | concluído com aviso “nenhuma fala detectada” | TXT vazio |
| `vazio.wav`, 00:00 | OpenAI pronto | inválido | nenhuma |

## Contraexemplos e edge cases

- extensão permitida com conteúdo de outro codec;
- duração detectável, mas stream sem áudio;
- arquivo removido entre validação e preparação;
- destino removido durante transcrição;
- nomes `arquivo`, `arquivo (1)` e `arquivo (2)` já existentes;
- cancelamento no instante em que o temporário ou saída é criado;
- resposta válida do provedor seguida de falha de disco;
- texto vazio para áudio válido e silencioso;
- caminho longo, Unicode e caracteres inválidos para nome de saída;
- aplicativo encerrado abruptamente com temporário existente.

## Compatibilidade, rollout e rollback

Não há migração de dados. A fatia não cria histórico. Configurações de provedor são dependências de specs próprias. Rollback remove a versão em desenvolvimento sem tocar saídas do usuário ou credencial protegida.

## Perguntas de clarificação

1. **Q1 [resolvida]:** fatia reduzida alinhada à arquitetura de referência, com portas e adaptadores e caminho OpenAI ponta a ponta primeiro.
2. **Q2 [resolvida]:** MP4, MP3 e WAV; entradas de vídeo têm somente o áudio extraído.
3. **Q3 [pendente]:** proposta: exibir um aviso explicativo na primeira utilização da OpenAI e manter, em toda execução, o indicador visível “OpenAI (cloud) — envia áudio e pode gerar custo”, sem abrir modal repetitivo. Clicar “Iniciar” com esse modo visível confirma o envio.
4. **Q4 [resolvida]:** API OpenAI com `whisper-1` primeiro; Whisper local entra depois como alternativa opcional para evitar custo de API.
5. **Q5 [resolvida]:** áudio válido porém silencioso gera TXT vazio com sucesso e aviso “nenhuma fala detectada”.

## Rastreabilidade

- PRD: RF-001, RF-004, RF-006, RF-008, RF-010, RF-011, RF-013, RF-014 e RF-015.
- Constituição: princípios 1 a 11.
- Riscos: R-001, R-002, R-004, R-006, R-007 e R-011.

## Gate da Fase 3

**NÃO ATENDIDO.** Q1, Q2, Q4 e Q5 foram resolvidas em 2026-07-31. Falta somente a decisão de UX/consentimento da Q3 antes de transformar a spec em contrato aprovado.
