# Constituição — Caleo Transcriber

- **Versão:** 0.1
- **Status:** proposta
- **Owner:** `caleo-hub`
- **Proposta em:** 2026-07-31
- **Aprovação:** pendente

## Precedência

Esta constituição governa regras estáveis. Comportamento aprovado vive no PRD e nas feature specs; decisões técnicas vivem em ADRs; instruções operacionais vivem em arquivos próprios. Uma fonte de menor nível não pode contrariar uma fonte superior. Em caso de conflito ou ausência de decisão crítica, o trabalho para e solicita decisão humana.

## Princípios estáveis

| # | Princípio | Motivação e consequência | Verificação |
|---:|---|---|---|
| 1 | Requisito aprovado precede mudança de comportamento | O agente não usa código para preencher decisão de produto ausente. Toda feature aponta para requisito e critério; mudança de comportamento atualiza spec, teste e documentação. | rastreabilidade no PR; teste ligado ao critério; ausência de questão crítica aberta |
| 2 | Privacidade é determinada pelo modo escolhido | O modo local não transmite mídia, texto ou telemetria. O modo OpenAI envia somente o áudio selecionado após ação explícita. | teste de rede no modo local; contrato do payload cloud; logs inspecionados |
| 3 | Segredos permanecem fora do domínio e das evidências | Chaves usam armazenamento protegido do Windows e nunca aparecem integralmente em UI, arquivo legível, log, teste, screenshot ou repositório. | secret scanning; teste de persistência e mascaramento; revisão de logs |
| 4 | Complexidade técnica não vira configuração obrigatória | Chunking, retries, limites e concorrência são automáticos. A aplicação usa limites reais do provedor e fronteiras naturais de fala, sem pedir tamanho de pedaço ao usuário. | jornadas abaixo, em e acima de 30 minutos; inspeção do plano automático |
| 5 | Regras do trabalho independem de UI, API e biblioteca | Fila, segmentos, estados, política de saída e recomposição não dependem de framework ou provedor. OpenAI e Whisper implementam a mesma fronteira de transcrição. | testes de domínio sem UI/rede; testes de contrato para ambos os provedores |
| 6 | Saídas são determinísticas, preservam timeline e não destroem dados | Recomposição usa offsets globais, mantém ordem, remove duplicação de sobreposição, não cria lacunas e alinha SRT à fonte original. Arquivo existente nunca é sobrescrito silenciosamente. | golden files; parser SRT; testes de fronteira/overlap; teste de colisão |
| 7 | Recursos e falhas são limitados por item | Um item falho não remove sucessos. Concorrência respeita CPU/GPU, memória, disco, API e custo. Cancelamento é seguro e temporários são recuperáveis/limpos. | testes de falha injetada, cancelamento, recuperação e limites de concorrência |
| 8 | Progresso e erros não podem enganar | Percentual só existe com base real; caso contrário, a UI mostra etapa indeterminada. Erros informam causa conhecida e ação possível sem revelar conteúdo ou segredo. | testes de estado; revisão de mensagens; acessibilidade do progresso |
| 9 | Dependências e builds são controlados | Toda dependência central possui justificativa, licença, versão e avaliação de manutenção. O executável é reproduzível e testado em Windows 10 x64 limpo. | lockfiles; inventário/SBOM; scanning; build e smoke test em VM limpa |
| 10 | Evidência é proporcional ao risco e não depende de autodeclaração | Mudanças pequenas apresentam comandos, resultados e riscos. Segurança, recomposição, provedores e distribuição exigem validação independente ou humana. | required checks; evidence pack; revisão do diff e dos artefatos |
| 11 | Operações sensíveis são humanas e reversíveis | O agente não decide política de dados, não usa mídia/chave real, não faz chamada paga ou release sem autorização. Mudanças destrutivas exigem alvo, backup e rollback. | matriz de permissões; aprovação registrada; ensaio de rollback |

## Ações que sempre exigem aprovação humana

- alterar política de envio, retenção, histórico ou telemetria;
- acessar chave, mídia ou transcrição real fora da execução iniciada pelo usuário;
- executar chamadas pagas de teste com a chave do usuário;
- adicionar ou substituir dependência central, decoder, runtime, modelo ou empacotador;
- mudar formatos públicos, timeline, política de nomes ou compatibilidade mínima;
- habilitar sobrescrita, exclusão, migração ou limpeza fora do diretório temporário controlado;
- assinar, publicar, distribuir ou atualizar um executável;
- reduzir required checks, aceitar risco alto residual ou emendar esta constituição.

## Required checks inegociáveis

Os comandos concretos serão definidos no harness das Fases 5 e 6. O pipeline deverá bloquear merge quando falhar:

1. formatação, lint e análise de tipos;
2. testes unitários de domínio e contratos de provedores;
3. testes de integração de mídia, saída, cancelamento e recuperação;
4. testes de aceitação das jornadas e da fronteira de 30 minutos;
5. teste de rede que comprove ausência de chamadas no modo local;
6. secret scanning, análise de dependências e licenças;
7. golden files TXT/SRT, parser SRT e testes de recomposição, overlap, retomada e deduplicação de chunks;
8. build do executável e smoke test em Windows 10 x64 limpo;
9. revisão humana proporcional para segurança, dados, dependências e release.

## Evidência suficiente

Uma fase ou tarefa só termina com: critérios atendidos identificados, comandos e resultados reais, diff resumido, riscos residuais, documentação atualizada e rollback aplicável. “Tudo passou” sem saída reproduzível não é evidência.

## Processo de exceção e emenda

Toda exceção ou alteração registra motivo, alternativas, impacto, riscos, owner, aprovador, data de vigência e plano para remover ou revisar a exceção. Emendas incrementam a versão e atualizam `docs/adoption/BOOK-TRACEABILITY.md`.

## Gate da Fase 2

**NÃO ATENDIDO.** `caleo-hub` precisa aprovar os onze princípios, as ações com aprovação obrigatória e os required checks.
