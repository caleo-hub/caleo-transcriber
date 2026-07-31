# Atributos de qualidade e fitness functions

- **Status:** proposta para aprovação
- **Data:** 2026-07-31

| Prioridade | Atributo | Cenário verificável | Fitness function planejada |
|---:|---|---|---|
| 1 | Privacidade | MP4 nunca sai do computador; somente áudio preparado alcança o provider | teste de contrato inspeciona payload e bloqueia extensão/container de vídeo |
| 2 | Segredo | chave não aparece em arquivos, logs, exceções ou pacote | secret scan + testes de redação + inspeção do artefato |
| 3 | Confiabilidade | falha/cancelamento nunca deixa TXT parcial ou sobrescreve arquivo | testes de falha injetada em cada etapa e escrita atômica |
| 4 | Responsividade | UI continua processando eventos durante mídia/rede/escrita | teste Qt com worker bloqueado e evento sentinela |
| 5 | Compatibilidade | pacote abre e executa smoke test em Windows 10 x64 limpo | job de build + teste em VM Windows 10 antes da release |
| 6 | Honestidade | percentual só existe quando há medida real | teste de projeção rejeita `known(percent)` sem total/progresso mensurável |
| 7 | Evolução | provider local pode ser adicionado sem alterar caso de uso | teste arquitetural impede imports de adapters no core |
| 8 | Usabilidade | primeiro trabalho configurável em até 3 minutos | roteiro de teste manual cronometrado |

## Checks obrigatórios antes de merge

1. formatação, lint e type check;
2. testes unitários e de contrato sem rede/chave real;
3. teste de dependências entre camadas;
4. secret scan e auditoria de logs;
5. teste de criação atômica/colisão/cancelamento;
6. build Windows x64 reproduzível no CI;
7. inventário de dependências e licenças.

Chamadas reais à OpenAI ficam fora do CI padrão: exigem chave e custo explicitamente aprovados e usam somente áudio sintético.

