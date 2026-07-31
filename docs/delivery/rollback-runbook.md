# Rollback de release Windows

## Owner e autoridade

`caleo-hub` decide pausar ou retirar uma versão de circulação. O agente pode preparar evidências
e comandos, mas não altera uma Release publicada sem autorização explícita.

## Gatilhos

- checksum, proveniência ou assinatura divergente;
- chave, conteúdo, caminho sensível ou erro bruto exposto;
- instalador não abre, não instala ou impede desinstalação;
- corrupção/sobrescrita de saída ou perda de arquivos do usuário;
- tráfego de rede durante o modo local;
- regressão crítica sem correção segura imediata;
- licença, SBOM ou componente nativo incompatível com a distribuição.

## Preparação obrigatória

Cada release registra versão, commit, digest, artefato anterior conhecido como bom e notas de
compatibilidade. A primeira release só pode avançar após ensaio de instalação/desinstalação; como
não existe versão anterior pública, seu rollback é interromper a distribuição e remover o
aplicativo, preservando credenciais e saídas.

## Procedimento

1. pausar novos downloads/promover a versão problemática como não recomendada;
2. preservar checksums, logs de CI e evidências redigidas;
3. comunicar claramente versão afetada, impacto e ação segura;
4. desinstalar a versão afetada sem apagar saída do usuário ou Credential Manager;
5. instalar o último artefato conhecido como bom e verificar seu checksum;
6. executar abertura, versão e smoke sintético;
7. confirmar que não houve migração, retenção ou efeito externo a compensar;
8. registrar resultado e decidir por correção ou nova publicação.

Não se apagam tags, artefatos ou evidências silenciosamente. Quando a segurança exigir retirada
imediata, a ação e sua justificativa ficam registradas no GitHub.

## Roll-forward

Use roll-forward quando a versão anterior também estiver vulnerável, quando o problema estiver
somente nas notas/metadados ou quando uma correção aditiva for mais segura que reinstalar. A nova
versão percorre o mesmo preflight, smoke e aprovação.

## Validação pós-rollback

- versão esperada abre pelo menu Iniciar;
- chave permanece no cofre e continua mascarada;
- arquivos de saída existentes permanecem intactos;
- nenhuma mídia temporária da tentativa fica retida;
- a jornada sintética aplicável passa;
- decisão e duração real do ensaio são registradas.

## RTO

Ainda desconhecido. A TASK-010 deve medir o ensaio completo e registrar um RTO real antes da
primeira publicação; não será inventado um prazo sem evidência.
