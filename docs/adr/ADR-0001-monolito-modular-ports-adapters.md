# ADR-0001 — Monólito modular com ports-and-adapters

- **Status:** aceito
- **Data:** 2026-07-31
- **Decisor:** `caleo-hub`

## Contexto

O produto é pessoal, desktop e entregue como um executável. Precisa trocar OpenAI por Whisper local no futuro e testar efeitos externos sem mídia, chave ou custo reais.

## Decisão proposta

Usar um monólito modular em processo único. O núcleo contém domínio e casos de uso; UI, mídia, providers, credenciais e filesystem são adapters ligados por portas explícitas.

## Consequências

- um deploy e diagnóstico simples;
- substituição de provider sem reescrever o fluxo;
- testes rápidos com fakes;
- disciplina de imports e composição obrigatória;
- pequeno custo de abstração somente nas fronteiras externas.

## Alternativas rejeitadas

- **UI chamando SDKs diretamente:** menor início, mas mistura estado, rede, mídia e segredo e dificulta o modo local.
- **Microsserviço/backend próprio:** não há escala, ownership ou deploy independente que justifique operação e superfície de ataque adicionais.
- **Plugin system genérico:** complexidade prematura; adapters internos cobrem a variação conhecida.
