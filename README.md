# Caleo Transcriber

Aplicativo desktop pessoal para Windows 10 x64 que extrai somente o áudio de MP4/MP3/WAV,
transcreve com a API OpenAI `whisper-1` e grava TXT ou SRT. Suporta fila de vários arquivos e divide
mídia longa automaticamente, sem configuração manual de chunks.

## Estado

A versão 0.3.1 corrige o contraste do menu de limpeza sob tema escuro do Windows. A fila mantém
seleção múltipla, remoção, limpeza, reordenação, repetição selecionada e pausa segura. Whisper local
e seleção de trecho permanecem para um incremento posterior. O instalador ainda não possui
assinatura Authenticode.

## Setup no Windows

Pré-requisito: Python 3.12 x64.

```powershell
.\setup.cmd
.\verify.cmd
.\.venv\Scripts\python.exe -m caleo_transcriber
```

Os scripts usam `.venv` e não exigem chave da OpenAI. Nenhum teste padrão realiza chamadas pagas ou envia mídia.

## Comandos canônicos

```powershell
.\format.cmd
.\verify.cmd
.\audit.cmd
```

O preflight de um futuro candidato de release, sem publicá-lo, usa:

```powershell
.\release-preflight.cmd -Version <versão-sem-v> -CandidateDirectory <diretório>
```

O build local do candidato, também sem publicar ou instalar, usa:

```powershell
.\build-package.cmd -Version 0.3.1
```

Ele exige a versão aprovada do Inno Setup e baixa o build FFmpeg fixado e verificado pelo projeto.

## Fontes de verdade

- comportamento: `specs/features/FEAT-001-transcribe-single-file.md` até `FEAT-003`;
- princípios: `specs/constitution.md`;
- arquitetura: `docs/architecture/` e `docs/adr/`;
- segurança: `docs/security/threat-model.md`;
- contrato do provider: `contracts/transcription-provider.md`;
- estado da adoção: `docs/adoption/STATUS.md`;
- plano do primeiro incremento: `docs/plans/first-increment.md` e `docs/tasks/`;
- segundo incremento e gates: `docs/plans/second-increment.md` e `docs/gates/`;
- instruções para agentes: `AGENTS.md`.
