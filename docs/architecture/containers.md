# Containers e implantação

- **Status:** proposta para aprovação
- **Data:** 2026-07-31

## Containers

```mermaid
C4Container
  title Containers do Caleo Transcriber
  Person(user, "Usuário")
  Container_Boundary(desktop, "Executável Windows x64") {
    Container(ui, "Desktop UI", "PySide6/Qt Widgets", "Apresenta estado e recebe comandos")
    Container(core, "Application Core", "Python", "Casos de uso, regras, estados e portas")
    Container(worker, "Worker", "QThreadPool + Python", "Executa mídia, rede e escrita fora da thread da UI")
    Container(media, "Media Adapter", "FFmpeg/ffprobe", "Inspeciona e extrai áudio")
    Container(out, "Filesystem Adapter", "Python/Windows", "Temporários e escrita atômica")
    Container(secret, "Credential Adapter", "Windows Credential Manager", "Protege a chave")
  }
  System_Ext(openai, "OpenAI API")

  Rel(user, ui, "Opera")
  Rel(ui, core, "Comandos e view state")
  Rel(core, worker, "Agenda tentativa/cancelamento")
  Rel(worker, media, "Inspeciona/extrai")
  Rel(worker, out, "Cria temporário e TXT")
  Rel(worker, secret, "Obtém chave")
  Rel(worker, openai, "Transcrição HTTPS")
```

## Implantação

- Um único pacote instalável para Windows 10 x64; nenhum serviço residente.
- Python e Qt são empacotados; o usuário não instala runtime ou usa terminal.
- `ffmpeg.exe` e `ffprobe.exe` são dependências nativas empacotadas e invocadas sem shell.
- Rede é usada somente pelo adaptador OpenAI e por funcionalidades futuras explicitamente autorizadas.
- A primeira escolha de empacotador é PyInstaller em modo `onedir`; `onefile` fica rejeitado inicialmente por pior diagnóstico, extração temporária no startup e maior complexidade com binários Qt/FFmpeg.

## Decisão de concorrência

A UI roda na thread principal. Cada tentativa roda em worker dedicado, com cancelamento cooperativo. Na primeira fatia existe no máximo uma tentativa ativa. Processos FFmpeg recebem handle explícito e são encerrados em cancelamento. A chamada HTTP possui timeouts finitos; seu cancelamento é de melhor esforço.

