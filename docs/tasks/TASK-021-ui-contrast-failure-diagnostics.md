# TASK-021 — Contraste e diagnóstico de falhas

## Objetivo

Garantir leitura completa da janela, tabela e configuração de chave sob tema escuro do Windows e
explicar a causa recuperável de cada item que falhar, sem expor caminho, mídia, transcrição ou chave.

## Contexto e fontes

O owner apresentou uma captura da beta 0.2.0 em que o diálogo herdava fundo escuro do Windows e
texto escuro da folha de estilo. Também relatou falha ao processar um MP4 válido, enquanto a UI
exibia somente “Falhou”. Aplicam-se FEAT-001/002/003, ADR-0002/0003 e o princípio constitucional de
que progresso e erros não podem enganar.

## Escopo de arquivos

- folha de estilo Qt da janela, diálogo, entradas, tabela, cabeçalho, seleção e estados desabilitados;
- diálogo de chave com largura mínima e folha de estilo explícita;
- estado textual e orientação de recuperação por categoria de falha, com código diagnóstico seguro;
- testes de UI e captura visual do diálogo corrigido.

## Restrições e autonomia

O vídeo informado pode ser lido e analisado localmente para diagnóstico, mas seu áudio não será
enviado à OpenAI. Nenhuma chave, caminho completo, conteúdo ou transcrição entra em evidência ou
log. A correção não publica uma nova release sem aprovação do owner.

## Critérios de aceitação

1. `QDialog`, `QLineEdit`, tabela e cabeçalho têm fundo e texto explícitos e legíveis, independentes
   do tema escuro do Windows.
2. O diálogo de chave não mistura fundo escuro com texto escuro e continua operável por teclado.
3. Um item falho mostra categoria em texto, orientação de recuperação e código diagnóstico seguro.
4. A mensagem de falha não contém caminho da fonte, chave ou conteúdo.
5. O MP4 relatado conclui probe, extração, checkpoint e saída com provedor substituto, sem upload.
6. Um smoke com mídia sintética diferencia credencial recusada de falha do arquivo sem registrar
   áudio ou transcrição.
7. `format.cmd`, `verify.cmd` e `audit.cmd` passam.

## Validação e evidência

Teste unitário da projeção de falhas e da folha de estilo, pipeline local com provedor substituto,
smoke OpenAI sintético e `docs/evidence/ux-increment-2/05-settings-dialog.png`.

## Rollback

Reverter somente a folha de estilo e a projeção de mensagens. Credenciais, checkpoints e saídas do
usuário não são migrados ou removidos.
