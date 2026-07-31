# Caleo Transcriber {{VERSION}} — beta de teste

Beta para Windows 10 22H2/Windows 11 x64. Selecione vários MP4, MP3 ou WAV, escolha TXT ou SRT e
acompanhe cada item em uma fila. Arquivos acima de 30 minutos são divididos automaticamente abaixo
da margem de upload, com timestamps, recomposição e retomada segura.

## Novidades desta beta

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

Confira `SHA256SUMS.txt` antes de instalar. Como esta é a primeira versão, rollback significa
desinstalar o aplicativo e interromper sua distribuição; a desinstalação não remove a chave do
Credential Manager nem arquivos TXT criados pela pessoa usuária.
