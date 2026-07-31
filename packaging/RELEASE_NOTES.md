# Caleo Transcriber {{VERSION}} — candidato não publicado

Primeira fatia para Windows 10 22H2/Windows 11 x64: selecione MP4, MP3 ou WAV de até 30 minutos,
use a OpenAI com chave protegida pelo Credential Manager e salve a transcrição em TXT.

## Privacidade e custo

- o modo OpenAI envia somente o áudio preparado após o clique em **Iniciar transcrição**;
- o uso da API pode gerar custo na conta da pessoa usuária;
- não há histórico persistente nem telemetria;
- chave, áudio e transcrição não entram em logs do aplicativo.

## Estado do candidato

- instalador inicialmente sem assinatura Authenticode do projeto;
- chamada real à OpenAI e smoke em VM Windows 10 x64 limpa dependem de gates separados;
- Whisper local, lote, segmentos e SRT pertencem aos próximos incrementos.

## Integridade e rollback

Confira `SHA256SUMS.txt` antes de instalar. Como esta é a primeira versão, rollback significa
desinstalar o aplicativo e interromper sua distribuição; a desinstalação não remove a chave do
Credential Manager nem arquivos TXT criados pela pessoa usuária.
