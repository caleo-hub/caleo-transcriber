# Contribuindo

1. Crie uma branch curta com prefixo `codex/` ou descrição equivalente.
2. Relacione a mudança a uma spec, ADR, risco ou contrato.
3. Faça setup com `.\setup.cmd`.
4. Mantenha o diff pequeno e sem arquivos de mídia, secrets ou artefatos de build.
5. Rode `.\verify.cmd` antes do commit.
6. Use commits objetivos e PR com objetivo, impacto, checks, riscos e rollback.

Mudanças de arquitetura, provider, dados, segurança, dependências centrais ou licenças exigem aprovação do owner. Chamadas reais à OpenAI exigem aprovação separada e mídia sintética/licenciada.
