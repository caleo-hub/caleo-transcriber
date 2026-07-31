# Brief da iniciativa — Caleo Transcriber

## Identificação

- **Data de abertura:** 2026-07-31
- **Estado:** proposta para validação humana
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
- O repositório GitHub do produto existe, está vazio, usa `main` como branch padrão e é público.

## Atores e contexto

- **Usuário primário — inferência:** pessoa usuária de Windows que precisa transcrever arquivos de áudio ou vídeo sem usar terminal.
- **Sponsor:** desconhecido.
- **Product owner:** Caleo é o candidato presumido, mas precisa aceitar explicitamente o papel.
- **Responsável técnico:** desconhecido.
- **Responsável por segurança, privacidade e operação:** desconhecido; pode ser acumulado pelo responsável técnico em um projeto individual, desde que isso seja declarado.

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
6. Transcrição por um provedor da OpenAI e por um mecanismo Whisper local.
7. Configuração persistente e protegida da chave da API.
8. Exportação em formatos ainda a escolher, com pelo menos um formato de texto.
9. Mensagens de erro acionáveis e histórico apenas da sessão, salvo decisão contrária.

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

## Perfil de adoção e risco

**Proposta: perfil padrão, com controles reforçados para segredo e dados locais.**

Justificativa: há integração externa, segredo persistente, possíveis dados pessoais/confidenciais, processamento concorrente, distribuição de binário e dependências nativas. O perfil não é crítico por padrão; deverá ser reclassificado se o produto for usado com dados regulados, em contexto corporativo obrigatório ou com alto impacto.

## Limites desta etapa

- Nenhum framework, linguagem, biblioteca de interface, empacotador, mecanismo de credenciais ou distribuição foi escolhido.
- Nenhum modelo ou endpoint específico da OpenAI foi selecionado.
- Nenhuma política de retenção, telemetria ou atualização foi presumida.
- Nenhum código de produto ou scaffold deve ser criado antes do gate da Fase 0.

## Decisões humanas necessárias para o gate

1. Quem aceita os papéis de product owner e responsável técnico?
2. O uso será pessoal, interno para uma equipe, comercial ou distribuição pública?
3. Quais dados podem ser enviados à OpenAI, e a aplicação deve manter algum histórico ou telemetria?
4. OpenAI e Whisper local precisam estar juntos no primeiro MVP, ou um modo deve ser entregue primeiro?
5. Quais formatos de entrada e saída são essenciais (por exemplo, TXT, SRT, VTT ou JSON), idiomas e necessidade de timestamps/locutores?
6. Quais versões mínimas do Windows e perfis de hardware devem suportar o modo local?

## Gate da Fase 0

**NÃO ATENDIDO.** O problema inicial, o perfil e os limites estão propostos, mas faltam aceite dos owners e respostas às seis decisões acima.
