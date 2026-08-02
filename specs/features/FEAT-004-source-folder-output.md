# FEAT-004 — Saída ao lado do arquivo original

- **Status:** proposta implementável
- **Owner:** `caleo-hub`
- **Risco:** baixo; evita configuração repetitiva em filas com muitas pastas

## Intenção

Permitir que a pessoa escolha salvar cada transcrição na mesma pasta do áudio ou vídeo de origem,
sem precisar escolher uma pasta comum para a fila.

## Regras

1. A opção é explícita na interface e não altera o modo cloud/local nem o envio de mídia.
2. Cada item usa a pasta do próprio arquivo de origem, mesmo quando a fila mistura diretórios.
3. O nome remove a extensão da mídia e acrescenta `_transcription`, preservando o formato escolhido:
   `Demo.mp4` produz `Demo_transcription.txt` ou `Demo_transcription.srt`.
4. A escrita atômica e a política existente de colisão permanecem ativas; nenhum arquivo é
   sobrescrito silenciosamente.
5. A opção não cria histórico, não copia a mídia e não remove a origem.
6. A escolha manual de pasta continua disponível e mantém o comportamento atual.

## Critérios de aceitação

- **SOURCE-CA-001:** marcar a opção habilita iniciar sem escolher uma pasta comum.
- **SOURCE-CA-002:** uma fila com origens em diretórios diferentes publica cada resultado no
  diretório correspondente.
- **SOURCE-CA-003:** TXT e SRT usam o sufixo `_transcription` e preservam a extensão de saída.
- **SOURCE-CA-004:** colisões continuam gerando nome exclusivo e preservando arquivos existentes.
- **SOURCE-CA-005:** desmarcar a opção permite escolher uma pasta comum e mantém `Demo.txt`/
  `Demo.srt` como comportamento legado.
- **SOURCE-CA-006:** a ação `Abrir pasta` de um item concluído abre a pasta efetiva daquele item.

