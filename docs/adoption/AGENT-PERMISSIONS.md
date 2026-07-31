# Matriz inicial de permissões do agente

Esta matriz limita ações por classe. Autorização para uma ação não se transfere automaticamente a outra sessão, ambiente ou recurso.

| Classe de ação | Estado atual | Limite |
|---|---|---|
| Ler o projeto local | permitido | somente dentro do `PROJECT_ROOT`, salvo fonte explicitamente indicada |
| Ler o livro e documentação pública | permitido | leitura progressiva das fontes da fase atual |
| Editar `docs/adoption/` | permitido | manter fatos, hipóteses, propostas e decisões distinguíveis |
| Editar código, configuração de build ou dependências | bloqueado | liberar somente após os gates de produto e arquitetura aplicáveis |
| Executar diagnósticos locais | permitido | comandos reversíveis e sem acesso a segredos |
| Instalar dependências ou executar binários baixados | requer aprovação | apresentar origem, licença, versão e finalidade |
| Acessar rede para documentação e GitHub | permitido | leitura; mutações somente quando solicitadas |
| Commit e push desta organização inicial | permitido nesta sessão | apenas os artefatos revisados, para `caleo-hub/caleo-transcriber` em `main` |
| Criar issues, branches adicionais, PRs ou releases | não autorizado | solicitar direção antes da mutação |
| Acessar ou receber a chave da OpenAI | proibido | o agente não deve pedir, revelar, copiar ou persistir a chave |
| Executar chamadas pagas à OpenAI | requer aprovação | informar finalidade, dados enviados e potencial de custo |
| Enviar mídia ou transcrição a serviço externo | autorizado somente no comportamento aprovado do produto | modo OpenAI por ação explícita, somente para o áudio selecionado; agentes e testes continuam usando conteúdo sintético por padrão |
| Usar mídia real fornecida pelo usuário | limitado | somente no escopo solicitado; não publicar nem reter sem política |
| Alterar configurações de produção, deploy ou assinatura | bloqueado | exige plano, evidências e aprovação humana específica |
| Excluir, sobrescrever ou migrar dados | requer aprovação explícita | alvo resolvido, backup/rollback e impacto informados |
| Delegar a outro agente | não autorizado por padrão | somente por solicitação explícita e com contrato de tarefa |

## Regras permanentes propostas

1. Segredos nunca entram no repositório, logs, screenshots, fixtures ou relatórios.
2. Mídia e transcrições reais não são usadas como fixtures de teste.
3. Dependências novas exigem justificativa, licença, versão e avaliação de manutenção.
4. Ações com custo, envio externo de dados ou efeito irreversível exigem aprovação humana.
5. O agente apresenta comandos e evidências reais; sua autodeclaração não encerra um gate.
6. Exceções devem registrar escopo, aprovador, prazo e forma de reversão.
7. O produto não mantém histórico persistente nem envia telemetria no MVP.

## Owner da matriz

Responsável técnico a definir. Até o aceite humano, prevalece o estado mais restritivo.
