# Visão — Caleo Transcriber

- **Status:** aprovada
- **Owner:** `caleo-hub`
- **Data:** 2026-07-31

## Situação atual

A evidência disponível é a descrição direta de um único usuário responsável pelo produto. Não existe ainda observação de jornada, medição de tempo ou aplicação anterior para comparação.

O usuário deseja transcrever arquivos locais no Windows com uma interface gráfica, podendo escolher processamento pela OpenAI ou por Whisper local. A forma atual de realizar esse trabalho e seu custo ainda não foram medidos.

## Problema

Uma pessoa que precisa converter vídeos ou áudios locais em texto no Windows encontra fricção quando a solução exige terminal, não permite escolher trechos e lotes, não esclarece uso de rede/custo ou não oferece controle simples sobre o destino dos resultados.

## Resultado esperado

Permitir que o usuário instale um executável no Windows 10, configure o mecanismo desejado e obtenha transcrições TXT ou SRT de arquivos inteiros ou segmentos, individualmente ou em lote, com progresso e falhas compreensíveis, sem histórico persistente ou telemetria.

## Atores e stakeholders

- **Usuário:** `caleo-hub`, no uso pessoal inicial.
- **Produto e aprovação:** `caleo-hub`.
- **Operação e suporte:** `caleo-hub`.
- **Segurança e privacidade:** `caleo-hub`.
- **Sistemas externos:** OpenAI API no modo cloud; biblioteca e modelos Whisper no modo local.

Os papéis devem ser revisitados antes de qualquer distribuição para terceiros.

## Proposta de valor

Uma única interface torna explícitas as escolhas que importam — arquivos, trecho, mecanismo, formato e destino — e mantém o estado de cada trabalho visível. O modo OpenAI favorece conveniência; o modo local permite processamento sem enviar áudio a um serviço após o modelo estar disponível.

## Métricas de sucesso candidatas

Como não haverá telemetria, as métricas serão verificadas por testes de aceitação, benchmarks locais e validação do owner.

| Métrica | Baseline | Meta aprovada | Evidência |
|---|---|---|---|
| Instalação e abertura em Windows 10 limpo | desconhecida | iniciar sem Python, terminal ou ambiente de desenvolvimento instalado pelo usuário | teste em VM limpa |
| Conclusão das jornadas críticas | inexistente | 100% das jornadas de referência passam antes da release | suíte de aceitação + validação humana |
| Primeiro trabalho configurado | desconhecida | até 3 minutos, excluindo download de modelo e tempo de transcrição | teste observado com owner |
| Segurança da chave | inexistente | zero ocorrência em repo, logs e configuração legível | secret scanning + testes |
| Privacidade local | inexistente | zero chamadas de rede durante transcrição local com modelo já instalado | teste de integração com rede observada |
| Isolamento de lote | inexistente | falha de um item não remove resultados concluídos nem bloqueia os demais | teste de aceitação |
| Correção dos formatos | inexistente | TXT legível e SRT válido nos casos de referência | golden files + parser SRT |
| Arquivo de referência | inexistente | vídeos de até 30 minutos integram a suíte obrigatória | teste de aceitação |
| Vídeo longo | inexistente | acima de 30 minutos, processamento automático sem configuração de divisão e com timeline preservada | teste de integração por fronteiras |
| Desempenho local | desconhecida | meta definida após benchmark por modelo/hardware | relatório de benchmark |

## Hipóteses

- **H1:** uma interface única é suficiente para as jornadas pessoais. **Como validar:** protótipo e execução das jornadas sem instrução externa.
- **H2:** oferecer os dois mecanismos no MVP compensa a complexidade adicional. **Como validar:** testes das mesmas amostras nos dois modos e avaliação do owner.
- **H3:** seleção de segmento reduz tempo e custo em arquivos longos. **Como validar:** comparar arquivo completo e segmento em amostras controladas.
- **H4:** fila por item reduz retrabalho em lotes com falha parcial. **Como validar:** injetar falha em um item intermediário.
- **H5:** TXT e SRT cobrem o uso pessoal inicial. **Como validar:** uso real pelo owner antes da primeira release.

## Restrições

- Windows 10 como versão mínima.
- Uso pessoal e operação por um único owner na primeira versão.
- OpenAI e Whisper local no mesmo MVP.
- Sem histórico persistente e sem telemetria.
- Somente o áudio escolhido pode sair da máquina no modo OpenAI, após ação explícita.
- A chave nunca deve ser versionada, exibida integralmente ou gravada em log.
- Requisitos de CPU/RAM serão derivados de benchmark; a fonte oficial só quantifica VRAM por modelo.
- O executável não deve exigir ambiente de desenvolvimento na máquina do usuário.
- Vídeos acima de 30 minutos devem ser tratados automaticamente; divisão e paralelismo são detalhes internos sujeitos a limites de recursos.

## Não objetivos do MVP

- Transcrição ao vivo, gravação de microfone ou reuniões.
- Editor completo de mídia ou transcrição.
- Tradução, resumo, dublagem ou geração de conteúdo.
- Contas, sincronização, colaboração ou armazenamento em nuvem.
- Histórico persistente, telemetria ou analytics.
- Plataformas diferentes de Windows.
- Atualização automática.
- Identificação de locutores.

## Riscos iniciais

O registro canônico está em [`docs/adoption/RISK-REGISTER.md`](../adoption/RISK-REGISTER.md). Os riscos dominantes são segredo da API, transferência de conteúdo, custo de lote, recursos do modo local, falha parcial, sobrescrita, dependências nativas e confiança no executável.

## Gate da visão

**ATENDIDO em 2026-07-31.** O owner aprovou os defaults, Windows x64, a meta de configuração e o comportamento esperado para vídeos longos.
