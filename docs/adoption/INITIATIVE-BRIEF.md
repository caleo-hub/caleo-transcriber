# Brief da iniciativa — Caleo Transcriber

## Identificação

- **Data de abertura:** 2026-07-31
- **Estado:** decisões humanas registradas; duas confirmações pendentes
- **Nome provisório:** Caleo Transcriber
- **BOOK_ROOT:** <https://github.com/caleo-hub/engenharia-de-software-com-agentes-de-codigo>
- **RUNBOOK:** <https://github.com/caleo-hub/engenharia-de-software-com-agentes-de-codigo/blob/main/guias-de-adocao/RUNBOOK-A-PRIORI-PROJETO-NOVO.md>
- **PROJECT_ROOT local:** `C:\Users\caleo\OneDrive\Área de Trabalho\Documentos\Transcritor de Vídeo`
- **Repositório do produto:** <https://github.com/caleo-hub/caleo-transcriber>

## Como ler este documento

- **Fato:** informação fornecida pelo responsável ou observada no repositório.
- **Inferência:** interpretação que precisa de confirmação.
- **Hipótese:** suposição a ser testada.
- **Proposta:** opção sugerida, ainda não aprovada.
- **Desconhecido:** decisão ou informação ausente.

## Problema inicial

**Proposta de frase de problema, sem solução embutida:** pessoas que precisam transformar vídeos locais em texto no Windows encontram fricção para obter transcrições com controle de trecho, privacidade, custo e destino dos resultados, especialmente quando não querem operar ferramentas de linha de comando.

Essa frase é uma inferência a partir das funcionalidades solicitadas e precisa ser validada pelo responsável do produto.

## Fatos observados

- O produto pretendido é um software para Windows distribuído como arquivo executável.
- A interface deve ser simples para transcrever um vídeo completo ou apenas um segmento.
- O usuário deve poder selecionar e processar vários arquivos.
- Deve haver indicadores de progresso.
- O usuário deve escolher o local de saída.
- Deve existir um modo de transcrição usando uma chave da API da OpenAI configurada uma vez.
- Deve existir também um modo de transcrição local baseado em Whisper.
- O repositório GitHub do produto existe, usa `main` como branch padrão e é público.
- `caleo-hub` assumiu os papéis de sponsor, product owner e responsável técnico.
- O uso inicial será pessoal.
- Não haverá histórico persistente nem telemetria.
- OpenAI e Whisper local devem integrar juntos o primeiro MVP.
- O usuário escolherá o formato de saída entre TXT e SRT.
- A versão mínima do sistema operacional será Windows 10.

## Atores e contexto

- **Usuário primário — inferência:** pessoa usuária de Windows que precisa transcrever arquivos de áudio ou vídeo sem usar terminal.
- **Sponsor:** `caleo-hub`, confirmado em 2026-07-31.
- **Product owner:** `caleo-hub`, confirmado em 2026-07-31.
- **Responsável técnico:** `caleo-hub`, confirmado em 2026-07-31.
- **Responsável por segurança, privacidade e operação:** `caleo-hub` no uso pessoal inicial; os papéis devem ser separados se o contexto de uso mudar.

## Resultado esperado

**Proposta:** permitir que o usuário obtenha transcrições de arquivos locais de forma compreensível e previsível, escolhendo entre processamento pela OpenAI e processamento local, sem expor credenciais e sem perder os resultados de trabalhos concluídos.

### Indicadores candidatos para a Fase 1

- Um usuário sem ambiente de desenvolvimento consegue instalar e iniciar o aplicativo.
- O usuário configura o modo de transcrição sem editar arquivos ou usar terminal.
- Um arquivo suportado pode ser transcrito por inteiro ou dentro de um intervalo válido.
- Um lote exibe o estado individual de cada item e preserva resultados concluídos se outro item falhar.
- A aplicação informa claramente quando dados serão enviados a um serviço externo.
- A chave da API não aparece na interface após ser salva, em logs, arquivos de configuração legíveis ou no repositório.

Os indicadores ainda precisam de metas mensuráveis de tempo, taxa de sucesso, formatos e qualidade.

## Primeira fatia de escopo candidata

1. Executável para uma versão mínima de Windows ainda a definir.
2. Seleção de um ou vários arquivos de áudio ou vídeo suportados.
3. Escolha entre arquivo completo e intervalo de início/fim por item.
4. Fila com progresso global e por arquivo, sucesso, falha e cancelamento seguro.
5. Escolha do diretório de saída e política explícita para conflitos de nome.
6. Transcrição por um provedor da OpenAI e por um mecanismo Whisper local no mesmo MVP.
7. Configuração persistente e protegida da chave da API.
8. Escolha por execução entre exportação TXT e SRT.
9. Mensagens de erro acionáveis, sem histórico persistente ou telemetria.

## Não objetivos candidatos para a primeira versão

- Aplicativos para macOS, Linux, web ou dispositivos móveis.
- Transcrição ao vivo de microfone ou reuniões.
- Editor completo de vídeo ou de transcrição.
- Sincronização em nuvem, contas de usuário ou compartilhamento colaborativo.
- Tradução, dublagem, resumo e geração de conteúdo.
- Identificação avançada de locutores, salvo se for elevada a requisito.
- Atualizador automático e marketplace de modelos.

Estes itens são propostas de corte de escopo, não decisões aprovadas.

## Dados e integrações

| Item | Classificação inicial | Tratamento esperado | Estado |
|---|---|---|---|
| Arquivos de entrada | potencialmente pessoais, confidenciais ou protegidos por direitos autorais | processar somente por ação explícita; informar quando houver envio externo | política pendente |
| Áudio temporário extraído | mesma classificação do arquivo de entrada | usar armazenamento temporário controlado e remoção segura após o trabalho | proposta |
| Transcrições | podem reproduzir dados sensíveis do conteúdo | salvar apenas no destino escolhido e evitar conteúdo em logs | proposta |
| Chave da API | segredo de alta sensibilidade | nunca versionar ou registrar; usar armazenamento protegido do Windows | proposta arquitetural |
| Configurações não secretas | baixa sensibilidade | persistência local versionada por schema | proposta arquitetural |
| OpenAI API | dependência externa com custo e transferência de dados | exigir escolha visível do modo e tratamento de limites/falhas | fato + proposta |
| Whisper local | dependência de CPU/GPU, memória, disco e modelo | validar compatibilidade e comunicar requisitos | fato + desconhecidos |

### Evidência oficial para o modo local

O repositório oficial `openai/whisper` declara Python 3.8–3.11, PyTorch recente e FFmpeg como requisitos de software. Ele publica memória aproximada de GPU por modelo, mas **não define mínimo formal de CPU ou RAM**:

| Modelos | VRAM aproximada publicada |
|---|---:|
| `tiny` e `base` | 1 GB |
| `small` | 2 GB |
| `medium` | 5 GB |
| `turbo` | 6 GB |
| `large` | 10 GB |

Fonte: [README oficial do OpenAI Whisper](https://github.com/openai/whisper/blob/main/README.md). A GPU não é declarada como obrigatória; portanto, o requisito mínimo de CPU/RAM e o tempo aceitável em Windows 10 deverão ser definidos por benchmark do aplicativo, não por estimativa do agente.

## Perfil de adoção e risco

**Proposta mantida, pendente de aceite explícito: perfil padrão, com controles reforçados para segredo e dados locais.**

Justificativa: há integração externa, segredo persistente, possíveis dados pessoais/confidenciais, processamento concorrente, distribuição de binário e dependências nativas. O perfil não é crítico por padrão; deverá ser reclassificado se o produto for usado com dados regulados, em contexto corporativo obrigatório ou com alto impacto.

## Limites desta etapa

- Nenhum framework, linguagem, biblioteca de interface, empacotador, mecanismo de credenciais ou distribuição foi escolhido.
- Nenhum modelo ou endpoint específico da OpenAI foi selecionado.
- A ausência de histórico persistente e telemetria foi decidida; retenção temporária e atualização ainda não foram definidas.
- Nenhum código de produto ou scaffold deve ser criado antes do gate da Fase 0.

## Decisões humanas registradas

1. `caleo-hub` acumula product owner e responsabilidade técnica no uso pessoal inicial.
2. O uso é pessoal.
3. Não haverá histórico persistente nem telemetria.
4. OpenAI e Whisper local integram juntos o primeiro MVP.
5. TXT e SRT serão opções de saída selecionáveis.
6. Windows 10 é o sistema operacional mínimo.
7. O requisito de hardware local usará dados oficiais quando existirem e benchmarks quando a biblioteca não publicar um mínimo.

## Confirmações necessárias para o gate

1. No modo OpenAI, autorizar o envio **somente do áudio do arquivo ou segmento escolhido**, por ação explícita do usuário. Sem essa autorização, o modo OpenAI precisa sair do MVP.
2. Aceitar ou corrigir a proposta de perfil de adoção **padrão**.

## Gate da Fase 0

**NÃO ATENDIDO.** Owners e escopo principal foram definidos. Faltam a política mínima de transferência do modo OpenAI e o aceite do perfil de adoção.
