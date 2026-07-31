# Validação da TASK-021

- **Data:** 2026-07-31
- **Branch:** `codex/task-021-ui-contrast-failure-diagnostics`
- **Escopo:** contraste do Qt e diagnóstico seguro de falhas por item

## Evidência do arquivo relatado

O arquivo MP4 informado pelo owner foi apenas lido localmente. `ffprobe` confirmou contêiner MP4,
vídeo H.264, áudio AAC estéreo a 48 kHz, 13.859.409 bytes e 110,717 segundos. O pipeline real de
probe, extração MP3, checkpoint e saída concluiu com provedor substituto. O arquivo e seu áudio não
foram enviados nem copiados para o repositório.

## Evidência OpenAI

A segunda de até cinco chamadas autorizadas usou somente voz sintética gerada para o teste. O
adapter retornou `category=credential` e `code=OPENAI_401`, sem imprimir ou salvar transcrição. Isso
separa a falha de credencial da mídia válida. Os dois temporários sintéticos foram enviados à
Lixeira após o teste; restam três chamadas autorizadas.

## Evidência visual e automatizada

- `docs/evidence/ux-increment-2/05-settings-dialog.png`: diálogo claro e legível sob tema escuro;
- 21 testes focais passaram após a correção;
- `verify.cmd`: 176 testes, Ruff, mypy, 3 contratos de importação, build e `pip check` aprovados;
- `audit.cmd`: nenhuma vulnerabilidade conhecida.

## Risco residual

A chave atual precisa ser substituída pelo owner antes de uma transcrição cloud funcionar. Nenhuma
nova beta foi construída, instalada ou publicada nesta tarefa.
