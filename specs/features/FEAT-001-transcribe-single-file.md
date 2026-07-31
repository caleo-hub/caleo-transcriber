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
- escolha explícita entre OpenAI e Whisper local já configurados;
- saída TXT no diretório escolhido;
- etapas e estado do trabalho;
- cancelamento de melhor esforço e repetição após falha;
- nome de saída seguro sem sobrescrita;
- limpeza de temporários e ausência de histórico.

## Fora de escopo

- configuração, teste ou remoção da chave da OpenAI;
- download e gestão de modelos locais;
- arquivos múltiplos e fila em lote;
- seleção de segmento;
- saída SRT;
- arquivos acima de 30 minutos e chunking externo;
- paralelismo;
- identificação de locutores, tradução ou edição;
- release/instalador final.

As capacidades acima continuam no MVP e receberão specs próprias.

## Atores e permissões

- **Usuário:** seleciona arquivo, provedor, destino e inicia/cancela/repete.
- **Aplicação:** pode ler somente a fonte escolhida, criar temporários controlados e gravar no destino escolhido.
- **OpenAI:** recebe somente o áudio preparado quando esse modo for explicitamente selecionado.
- **Whisper local:** processa mídia localmente sem chamadas de rede durante a transcrição.

## Pré-condições

1. Windows 10 x64.
2. Exatamente um provedor está selecionado e pronto:
   - OpenAI com credencial válida já protegida; ou
   - Whisper com modelo `base` já disponível.
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
3. O usuário escolhe OpenAI ou Whisper local já pronto.
4. O usuário escolhe o diretório de saída.
5. A interface apresenta arquivo, duração, provedor, formato TXT e destino antes do início.
6. O usuário inicia a transcrição.
7. A aplicação prepara somente o áudio necessário em temporário controlado.
8. O provedor produz texto e metadados mínimos de execução.
9. A aplicação normaliza o texto sem inventar ou resumir conteúdo.
10. A saída é gravada atomicamente no nome resolvido.
11. Temporários são removidos.
12. A interface mostra conclusão e o caminho do arquivo criado.

## Fluxos alternativos

### A1 — OpenAI

- O modo cloud permanece visível antes e durante o envio.
- Somente o áudio extraído é enviado; o vídeo original não é transmitido.
- Cancelamento após envio não promete revogar dados já transmitidos; impede etapas seguintes quando possível.

### A2 — Whisper local

- A transcrição não realiza chamadas de rede.
- CPU/GPU, modelo e etapa aparecem sem expor controles técnicos obrigatórios.
- Falta de recurso termina em erro acionável, sem derrubar a interface.

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
| modelo local ausente | não iniciar | abrir gestão de modelo |
| memória local insuficiente | cancelar inferência com segurança | fechar tarefas, trocar modelo ou repetir |
| falha ao salvar | não declarar sucesso; preservar texto apenas durante a tentativa | corrigir destino e repetir/salvar quando especificado |
| cancelamento | parar novas etapas; remover saída incompleta e temporários | iniciar nova tentativa |

## Regras e invariantes

1. Uma tentativa possui exatamente um arquivo, um provedor, um destino e um estado atual.
2. `concluído` implica um TXT final existente e legível.
3. Nenhum outro estado implica existência de saída final nova.
4. Arquivo preexistente nunca é alterado.
5. OpenAI recebe somente áudio derivado da fonte selecionada.
6. Whisper local não usa rede durante inferência.
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
  provider: openai | local
  output directory
  output format: txt
  state
  stage
  progress: known(percent) | indeterminate
  error category opcional
```

O contrato técnico, tipos de erro e portas serão definidos na arquitetura. Este modelo não autoriza persistência de histórico.

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

### CA-001 — TXT local

Dado um WAV sintético válido de até 30 minutos e modelo local pronto, quando o usuário iniciar no modo local, então um TXT UTF-8 deve ser criado no destino, a tentativa deve terminar `concluído` e nenhuma chamada de rede deve ocorrer.

**Evidência planejada:** teste de integração com rede observada e golden file.

### CA-002 — TXT OpenAI

Dado um MP3 sintético válido e credencial de teste autorizada, quando o usuário iniciar no modo OpenAI, então somente o áudio deve ser enviado e um TXT deve ser criado após resposta válida.

**Evidência planejada:** teste de contrato com provedor substituto; teste real separado e aprovado.

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
| `entrevista.wav`, 02:15 | local pronto | concluído | `entrevista.txt` |
| `aula.mp3`, 29:59 | OpenAI pronto | concluído | `aula.txt` |
| `aula.mp4`, 30:00 | local pronto | concluído | `aula.txt` |
| `aula.mp4`, 30:01 | qualquer | recusado nesta fatia | nenhuma; direcionar para feature longa |
| `vazio.wav`, 00:00 | qualquer | inválido | nenhuma |

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

1. **Q1 [bloqueadora]:** aprovar esta primeira fatia reduzida, deixando configuração, SRT, segmento, lote e mídia longa para incrementos seguintes?
2. **Q2 [produto]:** MP4, MP3 e WAV são suficientes para a primeira fatia, mantendo os demais formatos no MVP?
3. **Q3 [produto]:** escolher o modo OpenAI e clicar “Iniciar” é confirmação suficiente do envio, desde que a interface deixe o modo cloud visível, ou deve haver modal em toda execução? **Default recomendado:** sem modal repetitivo.
4. **Q4 [arquitetural]:** a primeira implementação deve validar os dois provedores ou começar pelo local e adicionar OpenAI no incremento seguinte? **Default recomendado:** contrato comum primeiro, local funcional primeiro, OpenAI logo depois.
5. **Q5 [preferência]:** áudio válido porém silencioso gera TXT vazio com sucesso ou aviso? **Default recomendado:** sucesso com aviso “nenhuma fala detectada”.

## Rastreabilidade

- PRD: RF-001, RF-004, RF-006, RF-008, RF-010, RF-011, RF-013, RF-014 e RF-015.
- Constituição: princípios 1 a 11.
- Riscos: R-001, R-002, R-004, R-006, R-007 e R-011.

## Gate da Fase 3

**NÃO ATENDIDO.** A implementação não deve ser planejada enquanto Q1 permanecer aberta. Q2–Q5 precisam de decisão antes de seus critérios virarem contratos e testes.
