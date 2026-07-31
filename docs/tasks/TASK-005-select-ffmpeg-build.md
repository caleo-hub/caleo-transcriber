# TASK-005 — Selecionar distribuição FFmpeg

## Objetivo

Investigar e recomendar versão/build Windows x64 com origem oficial/reputada, configuração de codecs, licença, checksum e estratégia reprodutível de aquisição.

## Contexto e fontes

ADR-0002; THIRD_PARTY; T-05/T-06/T-08; formatos MP4/MP3/WAV.

## Escopo de arquivos

Permitidos: `docs/adr/`, `THIRD_PARTY.md`, `scripts/` de verificação/download e fixtures de metadata. Proibidos: incorporar binário, implementar adapter ou aceitar licença silenciosamente.

## Restrições e autonomia

Investigação de risco moderado. Rede somente para fontes públicas. Nenhum binário entra no Git antes da aprovação do owner.

## Critérios de aceitação

Origem, versão, hash, licença LGPL/GPL, codecs necessários, tamanho, atualização e verificação documentados; pelo menos duas opções comparadas; recomendação reproduzível.

## Validação e evidência

Relatório, URLs primárias, hashes e prova do script em diretório ignorado.

## Rollback

Remover documentação/script; nenhum binário versionado.

