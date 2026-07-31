# FEAT-003 — Processamento em lote com fila isolada

- **Status:** aprovada
- **Owner:** `caleo-hub`
- **Risco:** moderado; alto quando combinado com custo cloud

## Intenção

Permitir selecionar vários arquivos, acompanhar cada resultado e continuar o lote quando um item
falhar, com cancelamento previsível e repetição apenas das falhas.

## Escopo

- diálogo multisseleção e arrastar/soltar MP4, MP3 e WAV;
- fila FIFO efêmera, com no máximo um item ativo;
- destino e formato TXT/SRT comuns à execução;
- estado e etapa por item, resumo do lote e ações acessíveis por teclado;
- seleção múltipla para remover, repetir e reorganizar itens;
- reordenação explícita somente entre itens pendentes;
- limpeza por escopo: concluídos, falhas/cancelados, pendentes ou toda a fila inativa;
- pausa segura após concluir o item ativo;
- cancelar pendentes, o item ativo ou o lote;
- preservar concluídos e repetir somente itens em `failed`.

Não entra: prioridade automática, execução paralela de arquivos, histórico após reinício, pastas
recursivas ou configurações diferentes por item. Mídia longa usa FEAT-002 internamente.

## Modelo e invariantes

Estados por item: `queued`, `preparing`, `transcribing`, `saving`, `completed`, `failed`,
`cancelling`, `cancelled`.

1. A fila preserva a ordem de seleção e elimina a mesma identidade de fonte duplicada.
2. No máximo um item está em estado ativo.
3. Falha/cancelamento de um item não altera saídas nem estados terminais dos demais.
4. O scheduler avança para o próximo item após sucesso, falha ou cancelamento do ativo.
5. Cancelar pendente não chama mídia, provedor ou filesystem de saída.
6. Cancelar o ativo é de melhor esforço e impede iniciar outro passo desse item.
7. `Repetir falhas` cria novas tentativas somente para os itens `failed`, na ordem original.
8. Itens `completed` nunca são reenviados ou sobrescritos pela repetição do lote.
9. O lote termina quando todos os itens estão em estados terminais.
10. Progresso global é contagem (`terminais/total`) e resumo textual, não estimativa de tempo.
11. Fechar e reabrir o aplicativo mostra fila vazia; retomada técnica só aparece ao selecionar
    novamente uma fonte compatível com FEAT-002.
12. Nenhum nome completo de caminho, conteúdo ou chave entra em log.
13. Reordenar altera somente a ordem relativa de itens `queued`; ativo e terminais não mudam de
    posição por essa ação.
14. Remover ou limpar uma linha descarta apenas metadados efêmeros da fila e nunca apaga origem,
    saída TXT/SRT ou credencial.
15. Pausar após o atual deixa os demais itens em `queued` e permite continuar depois.

## Fluxo principal

1. Usuário adiciona vários arquivos; inválidos permanecem visíveis com motivo seguro.
2. Escolhe TXT ou SRT e uma pasta de saída.
3. Revisa o indicador OpenAI cloud e inicia.
4. O primeiro item pronto fica ativo; os demais aguardam.
5. Cada item termina isoladamente e o scheduler segue automaticamente.
6. A interface mostra resumo de concluídos, falhos e cancelados e habilita `Repetir falhas` apenas
   quando houver falha.

## Critérios de aceitação

### BATCH-CA-001 — Seleção múltipla

Selecionar cinco arquivos cria cinco linhas na ordem escolhida; selecionar novamente a mesma fonte
não cria duplicata e informa o motivo.

### BATCH-CA-002 — Um ativo

Com vários itens prontos, nunca há mais de um em preparação/transcrição/salvamento.

### BATCH-CA-003 — Falha não interrompe lote

Se o segundo de quatro itens falhar, o primeiro permanece concluído e o terceiro começa.

### BATCH-CA-004 — Saídas preservadas

Falha, cancelamento ou repetição não altera arquivos finais produzidos por itens concluídos.

### BATCH-CA-005 — Cancelar pendente

Cancelar item `queued` o torna `cancelled` sem chamar provider e sem afetar a posição dos demais.

### BATCH-CA-006 — Cancelar ativo/lote

Cancelar ativo solicita interrupção segura. Cancelar lote também marca todos os pendentes como
cancelados; concluídos e falhos permanecem.

### BATCH-CA-007 — Repetir somente falhas

O comando fica desabilitado sem falhas. Quando acionado, somente itens `failed` voltam a `queued`
como novas tentativas e mantêm a ordem original.

### BATCH-CA-008 — Estados compreensíveis

Cada linha apresenta nome, duração quando conhecida, formato, estado textual e ação aplicável; cor
é apenas complementar e o foco por teclado é visível.

### BATCH-CA-009 — Progresso honesto

O lote mostra, por exemplo, “2 de 5 finalizados — 1 falhou”; o item ativo usa etapa e indicador
indeterminado quando não há total real.

### BATCH-CA-010 — Sem histórico

Ao reiniciar, a fila está vazia e nenhuma lista de trabalhos anteriores é apresentada.

### BATCH-CA-011 — Seleção e remoção

Seleção por linha aceita Ctrl/Shift. `Remover selecionados` remove itens pendentes ou terminais,
ignora o ativo com orientação visível e não apaga arquivos de entrada ou saída.

### BATCH-CA-012 — Reordenação previsível

`Subir` e `Descer` preservam a ordem interna da seleção e só trocam posições com outros itens
pendentes. O próximo processamento respeita a nova ordem.

### BATCH-CA-013 — Limpeza por escopo

É possível limpar concluídos, falhas/cancelados, pendentes ou toda a fila inativa. Durante uma
execução, o item ativo permanece visível e recebe uma explicação; a saída já criada é preservada.

### BATCH-CA-014 — Repetir selecionados

O comando habilita somente quando a seleção contém falha e não há execução ativa. Apenas falhas
selecionadas voltam a `queued`; concluídos, cancelados e pendentes selecionados não mudam.

### BATCH-CA-015 — Pausar após o atual

Durante processamento, `Pausar após o atual` não cancela o item ativo. Depois que ele termina, a
thread encerra e os demais itens continuam pendentes até `Iniciar fila`.

### BATCH-CA-016 — Cancelamento explícito

`Cancelar atual` solicita interrupção somente do item ativo. `Cancelar fila`, no menu de ações,
também cancela todos os pendentes. Nenhum dos comandos remove sucessos ou saídas.

## Exemplos e contraexemplos

Os vetores canônicos ficam em `contracts/examples/batch-queue-cases.json`. São contraexemplos:
parar a fila na primeira falha, reexecutar sucessos, ter dois itens ativos, apagar saída concluída,
mostrar percentual baseado em timer ou restaurar a fila inteira no próximo início.

## Gate

**ATENDIDO em 2026-07-31.** O owner aprovou `GATE-UX-002`: layout da tabela, ações, bloqueio de
configurações durante execução, resumo global e diálogo de retomada.
