# GATE-UX-002 — UX de fila, cancelamento e retomada

- **Status:** aprovado
- **Data da proposta:** 2026-07-31
- **Bloqueia:** TASK-018

## Fluxo proposto

- a área atual de arquivo vira uma tabela com colunas `Arquivo`, `Duração`, `Formato`, `Estado` e
  `Ação`; mostra apenas o nome, com caminho completo em tooltip acessível;
- `Adicionar arquivos` abre multisseleção; arrastar/soltar adiciona os formatos suportados;
- destino e formato TXT/SRT são comuns ao lote e ficam bloqueados enquanto ele executa;
- ações globais: `Iniciar fila`, `Cancelar fila` e `Repetir falhas`;
- cada pendente/ativo tem `Cancelar`; concluídos oferecem `Abrir pasta`; falhos exibem motivo e
  ação possível;
- resumo: “N de M finalizados — X concluídos, Y falharam, Z cancelados”; item ativo mostra etapa e
  indicador indeterminado quando não houver percentual real;
- falha não abre modal nem interrompe a fila; fica anunciada na linha e no resumo;
- ao selecionar fonte com checkpoint compatível, um banner pergunta `Continuar processamento
  interrompido?`, com ações `Continuar` e `Descartar e começar de novo`;
- upload ambíguo usa confirmação específica: `Esta parte pode já ter sido cobrada. Reenviar?`;
- reiniciar mostra tabela vazia, sem restaurar histórico.

## Acessibilidade exigida

Ordem de tabulação acompanha leitura, tabela e botões têm nomes acessíveis, foco é visível, estados
possuem texto e anúncios não dependem de cor. Escape não cancela trabalho sem confirmação.

## Evidência exigida depois da implementação

- testes pytest-qt de multisseleção, teclado, estados, bloqueios e ações;
- screenshot dos estados vazio, em execução, parcial com falha e retomada;
- teste de responsividade com worker;
- aceite visual/operacional do owner.

## Aprovação

- [x] tabela e controles globais aprovados;
- [x] comportamento de falha/cancelamento/repetição aprovado;
- [x] banners de retomada e upload ambíguo aprovados;
- [x] acessibilidade e resumo aprovados.

- **Owner/data:** `caleo-hub`, 2026-07-31
