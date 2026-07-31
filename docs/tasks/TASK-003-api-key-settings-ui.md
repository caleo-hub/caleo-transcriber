# TASK-003 — Tela de configuração da chave OpenAI

## Objetivo

Criar fluxo acessível para salvar, testar por validação não paga/local, substituir e remover a chave, exibindo somente estado mascarado.

## Contexto e fontes

TASK-002; RF-005/RF-006; decisão Q3; threat model; PRD de UX.

## Escopo de arquivos

Permitidos: `presentation/settings/`, caso de uso de credencial, bootstrap e testes Qt. Proibidos: chamada de transcrição, mídia e exibição integral após salvar.

## Restrições e autonomia

Risco moderado. Não validar chave com chamada paga nesta tarefa. Campo usa modo senha; clipboard e mensagens não repetem o valor.

## Critérios de aceitação

Operação por teclado; salvar/substituir/remover; indicador configurada/não configurada; máscara sem prefixo/sufixo real; aviso cloud no primeiro uso; testes com fake.

## Validação e evidência

`verify.cmd`; pytest-qt; checklist manual do owner para texto, foco e entendimento.

## Rollback

Reverter UI/caso de uso; adapter não perde credencial salvo fora de uma remoção explícita.

