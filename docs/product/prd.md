# PRD — Transcrição local e OpenAI v0.1

**Status:** em revisão  
**Owner:** `caleo-hub`  
**Data:** 2026-07-31

## Resumo executivo

Aplicativo desktop pessoal para Windows 10 que recebe um ou vários arquivos de áudio/vídeo, permite transcrever tudo ou um segmento, processa pela OpenAI ou pelo Whisper local e salva o resultado em TXT ou SRT no diretório escolhido. A interface mostra estado e progresso sem manter histórico ou enviar telemetria.

## Problema e evidências

A necessidade foi declarada pelo owner, mas ainda não possui baseline quantitativo. As funcionalidades solicitadas apontam fricção em cinco pontos: operação sem terminal, escolha de trecho, processamento em lote, alternativa cloud/local e controle de saída.

## Personas e atores

- **Pessoa usuária primária:** `caleo-hub`, usuária de Windows, operando arquivos locais.
- **Administrador e suporte:** a mesma pessoa no uso pessoal.
- **Serviço externo:** OpenAI API, somente quando o modo OpenAI for escolhido.
- **Processador local:** Whisper e dependências de mídia instaladas/empacotadas pelo aplicativo.

## Jornadas prioritárias

1. Instalar e abrir o aplicativo sem preparar ambiente de desenvolvimento.
2. Configurar, substituir, testar ou remover a chave da OpenAI sem vê-la novamente em texto aberto.
3. Selecionar um arquivo, escolher arquivo inteiro ou segmento e transcrever no modo desejado.
4. Selecionar vários arquivos, acompanhar cada item e preservar sucessos quando outro falhar.
5. Escolher TXT ou SRT e o diretório de saída antes de iniciar.
6. Baixar/selecionar um modelo local com tamanho, requisito e progresso compreensíveis.
7. Cancelar trabalhos pendentes e solicitar cancelamento seguro do item ativo.
8. Corrigir uma falha e repetir apenas os itens que falharam.

## Escopo do MVP

### Requisitos funcionais

| ID | Requisito | Estado |
|---|---|---|
| RF-001 | Selecionar arquivos por diálogo e arrastar/soltar | proposto |
| RF-002 | Adicionar vários arquivos a uma fila e remover itens antes do início | decidido |
| RF-003 | Escolher arquivo inteiro ou início/fim válidos por item | decidido; UX em aberto |
| RF-004 | Escolher explicitamente entre OpenAI e Whisper local | decidido |
| RF-005 | Salvar, substituir, testar e remover a chave da OpenAI em armazenamento protegido | decidido; mecanismo posterior |
| RF-006 | No modo OpenAI, enviar somente o áudio do arquivo/segmento escolhido | decidido |
| RF-007 | Instalar/selecionar modelo local com tamanho, progresso e erros visíveis | proposto |
| RF-008 | Escolher o diretório de saída | decidido |
| RF-009 | Escolher TXT ou SRT por execução | decidido |
| RF-010 | Exibir etapa, estado e progresso por item e do lote sem inventar precisão indisponível | decidido |
| RF-011 | Cancelar itens pendentes e fazer cancelamento de melhor esforço do item ativo | proposto |
| RF-012 | Repetir somente itens com falha | proposto |
| RF-013 | Nunca sobrescrever arquivo existente silenciosamente | proposto |
| RF-014 | Excluir temporários ao concluir, falhar ou cancelar, com recuperação no próximo início após encerramento abrupto | proposto |
| RF-015 | Não manter histórico persistente nem enviar telemetria | decidido |

### Atributos de qualidade

- **Usabilidade:** jornadas principais acessíveis em uma tela ou fluxo curto; erros devem dizer o que ocorreu e a ação possível.
- **Acessibilidade:** operação por teclado, foco visível, labels e progresso que não dependa apenas de cor.
- **Segurança:** chave protegida pelo Windows; segredo e conteúdo ausentes de logs; dependências verificadas.
- **Privacidade:** modo local sem chamadas de rede após modelo disponível; modo OpenAI visível e explícito.
- **Confiabilidade:** escrita atômica, isolamento por item e nenhuma sobrescrita silenciosa.
- **Compatibilidade:** Windows 10 x64 como baseline proposto; executável autocontido para o usuário.
- **Desempenho:** sem meta inventada; medir por modelo, CPU/GPU, duração e tamanho antes de definir limite.
- **Manutenibilidade:** fronteiras entre UI, fila, mídia, provedores e saída deverão ser verificáveis na arquitetura.

## Regras e invariantes

1. O modo local não transmite mídia, transcrição, chave ou telemetria.
2. O modo OpenAI transmite somente o áudio selecionado e somente após o usuário iniciar o trabalho nesse modo.
3. A chave da API nunca aparece integralmente depois de salva.
4. Um item falho não apaga nem invalida resultados de outros itens.
5. Arquivos existentes não são sobrescritos sem política aprovada e indicação visível.
6. Um segmento exige início menor que fim e fim dentro da duração detectada.
7. TXT e SRT derivam da mesma transcrição do item; o formato escolhido não dispara nova transcrição.
8. Percentuais só são exibidos quando há base real; caso contrário, mostrar etapa e atividade indeterminada.
9. Temporários não são tratados como histórico e devem ter ciclo de vida limitado ao processamento/recuperação.

## UX e acessibilidade

### Estrutura de interface proposta

- **Cabeçalho:** nome do aplicativo, acesso a configurações e indicação clara do modo atual.
- **Área de arquivos:** arrastar/soltar, adicionar arquivos e tabela/fila com nome, duração, trecho, estado e ações.
- **Painel de trabalho:** mecanismo, modelo local quando aplicável, idioma, formato e diretório de saída.
- **Rodapé de execução:** iniciar, cancelar, progresso global e resumo de sucessos/falhas.

### Estados necessários

Vazio, arquivo inválido, pronto, aguardando modelo, em preparação, enviando, transcrevendo, salvando, concluído, falhou e cancelado. Cada estado deve ter texto; cor e ícone são complementares.

## Dados, privacidade e retenção

- Nenhum histórico persistente de trabalhos.
- Nenhuma telemetria ou analytics.
- Configurações não secretas podem persistir localmente.
- Chave persiste apenas em armazenamento protegido do Windows.
- Temporários têm retenção limitada ao trabalho e limpeza de recuperação na próxima abertura.
- Saídas persistem somente no diretório escolhido.
- Conteúdo de arquivos e transcrições não entra em logs.

## Dependências e integrações

- OpenAI Transcription API; modelo e contrato serão decididos na fase de arquitetura com documentação oficial atual.
- `openai/whisper` local; seleção de modelos e empacotamento serão decididos após benchmark.
- FFmpeg ou capacidade equivalente para leitura/extração de mídia; escolha exige licença e avaliação de distribuição.
- Armazenamento protegido do Windows; mecanismo será decidido por ADR.

## Métricas e instrumentação

Não haverá coleta de produto. Evidências virão de:

- suíte de aceitação em VM Windows 10;
- testes de integração com provedores substituíveis;
- verificação de rede do modo local;
- secret scanning e inspeção de logs;
- parser de SRT e golden files;
- benchmarks locais versionados;
- validação manual do owner antes da release.

## Rollout e rollback

- Uso pessoal e instalação manual no MVP.
- Sem atualização automática.
- Release deve ser substituível pela versão anterior sem perder a chave ou saídas.
- Configurações persistentes precisarão de schema versionado e caminho de downgrade quando existirem.

## Defaults propostos para decisão

| Tema | Default proposto | Motivo |
|---|---|---|
| Idioma da interface | português do Brasil | contexto do owner |
| Entradas iniciais | MP4, MKV, MOV, AVI, MP3, WAV e M4A | cobre vídeo e áudio comuns; depende da validação do decoder |
| Idioma falado | detecção automática com opção manual | conveniência com controle para corrigir detecção |
| Timestamp de SRT em segmento | relativo ao arquivo original | permite usar o SRT sobre o vídeo original |
| Segmentos em lote | configuração por item; padrão “arquivo inteiro” | evita aplicar o mesmo intervalo a durações diferentes |
| Conflito de nome | gerar sufixo sem sobrescrever | preserva dados sem interromper o lote |
| Identificação de locutores | fora do MVP | reduz escopo e diferença entre provedores |
| Modelo local inicial | `base`, com seleção de outros modelos | requisito oficial baixo (~1 GB de VRAM) e escolha reversível; validar desempenho |
| Concorrência | um item ativo por vez no MVP | limita custo e pressão de CPU/GPU; paralelismo pode vir depois |

## Questões abertas

1. Os defaults acima são aceitos integralmente ou precisam de ajustes?
2. O limite “Windows 10” significa apenas x64 ou deve incluir ARM64?
3. A meta proposta de configurar o primeiro trabalho em até três minutos é útil?
4. Existe uma duração/tamanho de arquivo que obrigatoriamente deve funcionar no MVP?

## Critérios de saída do discovery

- visão e defaults aprovados pelo owner;
- jornadas prioritárias aceitas;
- pelo menos uma meta de usabilidade e um limite de arquivo definidos;
- não objetivos aceitos;
- nenhuma contradição crítica entre privacidade, modos e formatos;
- desconhecidos restantes podem ser resolvidos por spec ou arquitetura sem decisão de negócio oculta.

## Aprovações

- **Owner:** `caleo-hub`; aprovação do conteúdo pendente.
- **Gate da Fase 1:** não atendido.
