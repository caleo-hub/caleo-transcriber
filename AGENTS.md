# Instruções para agentes

## Comece aqui

Leia `docs/adoption/STATUS.md`, a spec aplicável, `specs/constitution.md`, `docs/architecture/modules.md` e os ADRs relacionados. Não use a conversa como única fonte de decisão.

## Comandos canônicos (PowerShell/Windows)

- setup: `.\setup.cmd`
- formatar: `.\format.cmd`
- verificar: `.\verify.cmd`
- auditar dependências: `.\audit.cmd`

Use Python 3.12 x64 da `.venv`. Testes padrão não usam rede, chave real ou mídia pessoal.

## Limites arquiteturais

- `domain` não depende de framework ou infraestrutura;
- `application` depende apenas de `domain`;
- UI e adapters dependem das portas, nunca o inverso;
- OpenAI, FFmpeg, Credential Manager e filesystem entram por adapters;
- nunca use `shell=True` para mídia;
- nunca registre chave, headers, conteúdo, transcrição ou caminhos sensíveis;
- não invente progresso percentual.

## Escopo e aprovação

Pode ler, editar e testar localmente dentro do repositório. Requer aprovação explícita antes de: usar secrets, chamar API paga, enviar mídia, instalar/publicar release, alterar política de dados, aceitar licença nova, fazer deploy ou executar exclusão material. Preserve mudanças não relacionadas do usuário.

## Pronto para revisão

Diff pequeno e rastreável; spec/ADR atualizados quando necessário; `.\verify.cmd` passa; nenhuma credencial ou mídia real no diff; riscos e verificações relatados com evidência.
