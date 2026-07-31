# Caleo Transcriber {{VERSION}} — beta de teste

Beta para Windows 10 22H2/Windows 11 x64. Selecione vários MP4, MP3 ou WAV, escolha TXT ou SRT e
acompanhe cada item em uma fila. Arquivos acima de 30 minutos são divididos automaticamente abaixo
da margem de upload, com timestamps, recomposição e retomada segura.

## Novidades desta beta

- contraste corrigido no diálogo, campos, tabela e cabeçalhos mesmo com tema escuro do Windows;
- falhas mostram categoria, ação de recuperação e código seguro, inclusive chave OpenAI recusada;
- o botão de chave agora informa corretamente que verifica apenas o formato local;
- fila FIFO: um item ativo, falhas isoladas, cancelamento e repetição somente das falhas;
- mídia longa por tamanho real, silêncio próximo à fronteira e overlap conservador;
- checkpoint temporário protegido pelo DPAPI, com expiração em sete dias;
- TXT e SRT consolidados, atômicos e sem sobrescrever saídas existentes;
- novo ícone próprio na janela, executável, atalhos e instalador;
- chave configurada uma vez no Windows Credential Manager.

## Privacidade e custo

- o modo OpenAI envia somente o áudio preparado após o clique em **Iniciar fila**;
- o uso da API pode gerar custo na conta da pessoa usuária;
- não há histórico persistente nem telemetria;
- chave, áudio e transcrição não entram em logs do aplicativo.

## Estado da beta

- instalador inicialmente sem assinatura Authenticode do projeto;
- instalador sem assinatura Authenticode: o Windows pode mostrar aviso de editor desconhecido;
- Whisper local e seleção de trecho ainda não fazem parte desta beta;
- não há telemetria, histórico persistente ou atualização automática.

## Integridade e rollback

Confira `SHA256SUMS.txt` antes de instalar. O rollback recomendado é desinstalar esta versão e
reinstalar `v0.2.0-beta.1`; a desinstalação não remove a chave do Credential Manager nem arquivos
TXT/SRT criados pela pessoa usuária.
