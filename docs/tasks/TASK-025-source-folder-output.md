# TASK-025 — Saída automática na pasta de origem

## Objetivo

Adicionar uma alternativa de destino para filas grandes: salvar cada transcrição ao lado do
arquivo original com nome previsível e sem sobrescrita.

## Contexto e fontes

Solicitação do owner em 2026-08-02; PRD RF-008, FEAT-003, constituição e política de escrita
atômica do adapter de filesystem.

## Escopo de arquivos

`application/batch.py`, `application/transcribe_long_media.py`, `presentation/main_window.py`,
testes de fila/UI/saída, FEAT-004 e documentação do PRD.

## Restrições e autonomia

Não alterar envio cloud/local, credenciais, telemetria, mídia de origem ou política de sobrescrita.
Não acessar chave ou mídia pessoal, instalar o aplicativo ou publicar release nesta tarefa.

## Escopo

- `BatchSettings` e comando de mídia longa com destino por item e sufixo de nome;
- checkbox acessível na janela principal;
- abertura da pasta efetiva do resultado concluído;
- spec, testes unitários/aceitação/integração e documentação.

## Fora de escopo

Persistência da preferência, subpastas recursivas, alterações no contrato cloud/local, renomeação
de saídas manuais ou exclusão de arquivos existentes.

## Critérios de aceitação

1. A opção habilita iniciar sem pasta comum e usa a pasta de cada fonte.
2. O nome automático acrescenta `_transcription` antes da extensão de saída.
3. TXT/SRT, colisões, cancelamento e escrita atômica preservam as políticas existentes.
4. A pasta efetiva pode ser aberta pela ação do item concluído.
5. O modo manual permanece compatível.

## Verificação

Foco: `tests/acceptance/test_batch_processor.py`, `tests/acceptance/test_transcribe_long_media.py`,
`tests/integration/test_atomic_transcript_output.py` e `tests/unit/test_main_window.py`; depois
`verify.cmd` e `audit.cmd`.

## Validação e evidência

Testes focais, `verify.cmd`, `audit.cmd`, diff sem credenciais/mídia e revisão da jornada da fila.

## Rollback

Reverter a opção e os testes/documentação. Saídas já criadas permanecem intocadas.
