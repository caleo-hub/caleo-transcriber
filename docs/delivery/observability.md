# Observabilidade local e privacidade

- **Status:** definido para implementação incremental
- **Owner:** `caleo-hub`
- **Escopo:** aplicativo desktop pessoal, sem backend, histórico ou telemetria

## Adaptação operacional

Não haverá envio de logs, métricas, traces, crash dumps ou analytics. Dashboards e alertas
remotos não são proporcionais a um aplicativo pessoal sem serviço operado. A evidência de
saúde combina estado visível na UI, checks do GitHub, testes automatizados e validação manual
do candidato em Windows 10 x64.

## Sinais visíveis durante a sessão

A UI deve apresentar, sem persistir histórico:

- etapa atual e estado terminal de cada item;
- quantidade de itens na fila, concluídos, falhos e cancelados;
- categoria de erro e ação recomendada;
- provedor selecionado e indicador cloud permanente quando aplicável;
- progresso determinado somente quando existir medida real.

Esses sinais vivem em memória durante a execução. Fechar o aplicativo os descarta.

## Diagnóstico local

O diagnóstico fica desligado por padrão. Uma ação explícita poderá criar um relatório em local
escolhido pelo usuário, contendo apenas eventos estruturados e redigidos. O aplicativo não o
envia automaticamente.

Campos permitidos:

- versão do aplicativo e do schema de eventos;
- identificadores aleatórios e efêmeros de sessão/operação;
- instante, severidade, etapa, resultado, duração e código de erro próprio;
- provedor (`openai` ou `local`) e tipo genérico de mídia (`audio` ou `video`).

Campos proibidos:

- chave, headers, corpo de request/response ou erro bruto de SDK;
- áudio, vídeo, transcrição ou qualquer trecho de conteúdo;
- nome e caminho de arquivo, diretório de saída ou nome de usuário do Windows;
- modelo local instalado, identificadores de máquina ou informação destinada a fingerprinting.

Canários automatizados devem provar que os campos proibidos não aparecem no buffer, relatório,
stdout, stderr nem pacote.

## Indicadores e objetivos de release

Sem uma população observada, SLO mensal e error budget seriam números inventados. Até existir
evidência suficiente, o gate usa objetivos binários:

1. 100% das jornadas críticas de referência passam no candidato;
2. zero ocorrência dos canários de chave e conteúdo nas evidências inspecionadas;
3. instalação, abertura, transcrição sintética, gravação, cancelamento e desinstalação passam na
   VM Windows 10 x64;
4. o primeiro trabalho permanece configurável em até três minutos no teste observado do owner.

Tempos de inicialização e transcrição serão registrados como baseline antes da primeira release,
sem estabelecer meta retrospectiva para fazer o resultado parecer aprovado.

## Ações quando um sinal falha

- falha em CI, secret scan, checksum, SBOM ou preflight bloqueia o candidato;
- falha na VM, vazamento, corrupção de saída ou rede no modo local aciona rollback;
- lentidão sem perda/corrupção bloqueia avanço até ser classificada pelo owner;
- toda decisão pós-validação é registrada como `avançar`, `pausar`, `rollback` ou `roll-forward`.
