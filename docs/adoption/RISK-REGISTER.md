# Registro inicial de riscos

Escala provisória: probabilidade **B** (baixa), **M** (média), **A** (alta) ou **?** (desconhecida); impacto **B**, **M**, **A** ou **C** (crítico). As classificações precisam de revisão humana.

| ID | Risco | Prob. | Impacto | Resposta proposta | Owner | Estado |
|---|---|---:|---:|---|---|---|
| R-001 | A chave da OpenAI ser exposta em configuração legível, log, erro, pacote ou repositório público | M | C | armazenamento protegido do Windows; mascaramento; secret scanning; testes que vetem vazamento | técnico | aberto |
| R-002 | Conteúdo pessoal, confidencial ou protegido ser enviado à OpenAI sem compreensão do usuário | M | A | enviar somente o áudio do arquivo/segmento escolhido; aviso inicial e indicador cloud persistente propostos; sem histórico ou telemetria | produto + privacidade | decisão de UX Q3 pendente |
| R-003 | Arquivos grandes ou lotes provocarem custo de API inesperado | M | A | estimativa/preflight quando possível; confirmação; limites configuráveis; estado e custo observáveis | produto | aberto |
| R-004 | Whisper local falhar ou tornar a máquina inutilizável por falta de CPU, GPU, memória ou disco | A | M | usar a tabela oficial de VRAM (1–10 GB conforme modelo) e definir CPU/RAM/tempo por benchmark em Windows 10; limitar concorrência e permitir cancelamento | técnico | aberto |
| R-005 | Falha de um item interromper o lote ou perder resultados concluídos | M | A | estado por item; isolamento de falhas; escrita atômica; retomada/repetição segura | técnico | aberto |
| R-006 | Arquivos existentes no destino serem sobrescritos ou nomes colidirem | M | A | política visível de conflito; nomes determinísticos; confirmação; nunca sobrescrever silenciosamente | produto + técnico | aberto |
| R-007 | Dependências nativas de mídia, IA ou empacotamento introduzirem vulnerabilidade, licença incompatível ou build não reproduzível | M | A | inventário/SBOM; versões controladas; licença; scanning; builds reproduzíveis | técnico | aberto |
| R-008 | Intervalos inválidos, unidades ambíguas ou diferenças entre itens produzirem transcrições erradas | M | M | validação por duração; formato de tempo inequívoco; preview e critérios de borda | produto | aberto |
| R-009 | Download e armazenamento de modelos locais consumirem espaço ou rede sem transparência | A | M | informar tamanho e origem; consentimento; progresso; integridade; remoção controlada | produto + técnico | aberto |
| R-010 | Executável não assinado ou distribuição informal reduzir confiança e gerar alertas do Windows | M | M | definir canal de distribuição, assinatura e política de release antes da entrega pública | produto + técnico | aberto |
| R-011 | Logs, dumps ou mensagens de erro incluírem nomes de arquivos, trechos ou transcrições sensíveis | M | A | logging mínimo e estruturado; redaction; opt-in para diagnóstico; revisão de dumps | técnico + privacidade | aberto |
| R-012 | A qualidade variar por idioma, ruído e modelo sem o usuário entender limitações | A | M | declarar limites; amostras/evals sintéticos ou licenciados; opção de idioma e timestamps conforme spec | produto | aberto |
| R-013 | Divisão ou paralelismo de vídeos longos gerar lacunas, duplicações, texto fora de ordem ou timestamps incorretos | M | A | corte preferencial em silêncio, overlap controlado, offsets globais, merge/deduplicação determinísticos, checkpoints e concorrência limitada | técnico | estratégia candidata documentada |

## Riscos que impedem aumento de autonomia

- R-001 e R-002 impedem implementar persistência de credencial ou integração externa sem decisões de segurança e dados.
- R-006 impede implementar escrita de saída sem política de conflito.
- R-007 impede escolher e empacotar dependências centrais sem avaliação arquitetural.
- R-010 impede release público antes de uma decisão de distribuição e confiança do binário.
- R-013 impede implementar chunking/paralelismo sem contrato de recomposição e testes de fronteira.
