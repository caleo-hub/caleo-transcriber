# Caleo Transcriber

Aplicativo desktop pessoal para Windows 10 x64 que extrai áudio de MP4/MP3/WAV, transcreve inicialmente com a API OpenAI `whisper-1` e grava TXT. Whisper local, SRT, segmentos, lotes e mídia longa entram em incrementos posteriores.

## Estado

O repositório contém o harness e o scaffold arquitetural. A feature ainda não está implementada.

## Setup no Windows

Pré-requisito: Python 3.12 x64.

```powershell
.\setup.cmd
.\verify.cmd
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

## Fontes de verdade

- comportamento: `specs/features/FEAT-001-transcribe-single-file.md`;
- princípios: `specs/constitution.md`;
- arquitetura: `docs/architecture/` e `docs/adr/`;
- segurança: `docs/security/threat-model.md`;
- contrato do provider: `contracts/transcription-provider.md`;
- estado da adoção: `docs/adoption/STATUS.md`;
- plano do primeiro incremento: `docs/plans/first-increment.md` e `docs/tasks/`;
- instruções para agentes: `AGENTS.md`.
