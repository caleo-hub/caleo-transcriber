# ADR-0002 — Stack desktop Windows

- **Status:** aceito
- **Data:** 2026-07-31
- **Decisor:** `caleo-hub`

## Decisão proposta

- Python 3.12 x64 como runtime de desenvolvimento;
- PySide6 com Qt Widgets para a interface;
- OpenAI Python SDK no adapter cloud;
- FFmpeg/ffprobe como binários empacotados para probe e extração;
- Windows Credential Manager por adapter baseado em `keyring`;
- PyInstaller `onedir` para empacotar a primeira release.

Versões serão travadas com hashes na Fase 5 após prova de build em Windows 10 x64.

## Por quê

Python reduz atrito para o futuro Whisper local; PySide6 oferece desktop nativo e workers integrados; FFmpeg cobre os contêineres aprovados; `onedir` favorece transparência e diagnóstico de dependências nativas.

## Alternativas

- **.NET/WPF:** excelente integração Windows e segredo, mas adicionaria uma segunda stack ou ponte para o Whisper local em Python. Rejeitada para evitar fronteira de processo prematura.
- **Tauri/webview:** binário leve, mas cria duas stacks e integração adicional com worker/ML. Rejeitada para esta escala.
- **Tkinter:** menor dependência, mas componentes, acessibilidade e apresentação de estados complexos são mais limitados. Rejeitada.
- **PyInstaller onefile:** distribuição visualmente simples, mas startup, antivírus e extração temporária de binários nativos complicam diagnóstico. Adiada; poderá ser reavaliada após o MVP.

## Riscos e gates

- confirmar licenças e forma de redistribuição de Qt/PySide6 e do build específico de FFmpeg;
- provar build e execução em VM Windows 10 x64;
- provar que Credential Manager funciona no pacote;
- medir tamanho, startup e falso positivo de antivírus antes da release.
