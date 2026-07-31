# GATE-SEC-002 — Segurança de mídia longa e lote

- **Status:** pendente de aprovação do owner
- **Data da proposta:** 2026-07-31
- **Bloqueia:** TASK-012 até TASK-017

## Decisões para aprovação

1. Cada upload contém somente MP3 de áudio, usa nome neutro e tem menos de 24 MB.
2. Chunks cloud são sequenciais no incremento; concorrência de upload é exatamente um.
3. Retry automático não ocorre após upload iniciado. Estado ambíguo exige confirmação explícita para
   possível reenvio/custo.
4. Checkpoint fica em `%LOCALAPPDATA%`, sem caminho completo nem texto no manifesto. Resultado
   parcial é cifrado com DPAPI do usuário atual.
5. Checkpoint recuperável expira em sete dias; sucesso/cancelamento/incompatibilidade remove tudo.
   Áudio abandonado é removido no próximo início e nunca é preservado para retomada.
6. Fingerprint e hash de parâmetros impedem misturar fonte/configuração alterada.
7. Fila é efêmera, sem histórico/telemetria; logs contêm somente códigos, IDs efêmeros, estados e
   contagens.

## Evidência exigida depois da implementação

- spy prova tipo/tamanho/nome de todos os uploads;
- testes de crash em `pending`, `uploading` e `confirmed`;
- canários ausentes do manifesto/log e presentes apenas no blob DPAPI indecifrável por outro escopo;
- adulteração/fingerprint incompatível rejeitados;
- cleanup em sucesso, cancelamento, expiração e startup;
- contador prova no máximo um request cloud ativo;
- nenhuma chamada paga, chave ou mídia pessoal no CI.

## Risco residual

OpenAI recebe o áudio iniciado pelo usuário; malware na mesma conta pode acessar mídia/memória;
DPAPI não protege durante o processo; confirmação de reenvio pode gerar custo duplicado se o upload
anterior tiver sido processado. Esses riscos devem ficar claros na ação de retomada.

## Aprovação

- [ ] limites e concorrência aprovados;
- [ ] retenção de sete dias e DPAPI aprovadas;
- [ ] tratamento de upload ambíguo aprovado;
- [ ] risco residual aceito.

- **Owner/data:** pendente
