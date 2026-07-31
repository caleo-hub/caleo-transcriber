# Runbook de release Windows

## Modelo de entrega

O produto não possui deploy de servidor nem atualização automática. O rollout proporcional é:

1. **PR:** validações sem secret, rede paga ou mídia pessoal;
2. **artefato de CI:** pacote temporário, não publicado, inspecionado pela TASK-010;
3. **candidato do owner:** instalação do mesmo digest em VM Windows 10 x64 limpa;
4. **release:** publicação manual e aprovada no GitHub Releases;
5. **observação:** download, checksum, instalação e smoke do arquivo publicado;
6. **decisão registrada:** avançar, pausar, rollback ou roll-forward.

Não há coortes ou feature flags remotas. O candidato restrito ao owner cumpre a função de canary.

## Convenções

- tags e versões usam SemVer: `vMAJOR.MINOR.PATCH`;
- versões anteriores permanecem identificáveis e instaláveis para rollback;
- o build é feito uma vez; validação e publicação promovem o mesmo digest;
- o workflow de release será manual e exigirá aprovação do owner;
- branch, tag e notas devem apontar para o commit validado.

## Conteúdo obrigatório do candidato

- `CaleoTranscriber-Setup-<versão>-x64.exe`;
- `SHA256SUMS.txt`;
- `sbom.spdx.json`;
- `THIRD_PARTY.md`;
- `RELEASE_NOTES.md`.

O preflight local é executado com:

```powershell
.\release-preflight.cmd -Version <versão-sem-v> -CandidateDirectory <diretório>
```

Esse comando verifica presença, arquivos não vazios, JSON do SBOM e checksum do instalador. Ele
não substitui assinatura, varredura antimalware, inspeção do pacote ou smoke em VM.

## Checklist antes da publicação

- [ ] TASK-002 até TASK-010 aceitas e mescladas;
- [ ] commit candidato com CI, auditoria e secret scan verdes;
- [ ] dependências travadas, SBOM e licenças revisadas;
- [ ] FFmpeg aprovado com origem, licença e checksum;
- [ ] instalador criado em runner Windows a partir do commit candidato;
- [ ] preflight e inspeção de segredo/conteúdo aprovados;
- [ ] instalação e desinstalação em Windows 10 x64 limpo aprovadas;
- [ ] smoke da jornada cloud com áudio sintético aprovado mediante autorização específica;
- [ ] modo local sem conexão de saída comprovado quando entrar na release;
- [ ] acessibilidade por teclado e configuração em até três minutos validadas pelo owner;
- [ ] decisão sobre Authenticode registrada;
- [ ] rollback ensaiado com a versão anterior;
- [ ] owner aprovou a publicação no sistema que executará a release.

## Validação após publicar

1. baixar os artefatos do GitHub Releases em ambiente limpo;
2. verificar `SHA256SUMS.txt` sobre o arquivo baixado;
3. instalar sem Python, Qt ou ferramentas de desenvolvimento preexistentes;
4. abrir pelo menu Iniciar e confirmar versão;
5. executar smoke sintético autorizado;
6. confirmar ausência de chave, mídia e transcrição em pacote, stdout, stderr e diagnóstico;
7. desinstalar e confirmar que arquivos de saída do usuário e credencial não foram apagados;
8. registrar evidências e uma das quatro decisões previstas.

## Critérios de interrupção

Não publicar ou interromper a distribuição se houver checksum divergente, segredo/conteúdo no
artefato, falha de instalação/abertura, saída corrompida, transmissão no modo local, licença
ausente, antivírus bloqueador não avaliado ou impossibilidade de executar o rollback.
