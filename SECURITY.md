# Segurança

## Reporte

Não abra issue pública com chave, áudio, transcrição, caminho pessoal ou detalhe explorável. Contate o owner `caleo-hub` pelo canal privado associado ao repositório.

## Regras obrigatórias

- chave somente no Windows Credential Manager;
- nenhum secret em `.env`, log, teste, fixture ou commit;
- nenhuma mídia pessoal no repositório;
- somente áudio preparado pode alcançar o adapter OpenAI;
- subprocessos recebem lista de argumentos e `shell=False`;
- dependências e binários nativos exigem versão, origem e licença registradas;
- uma vulnerabilidade relevante bloqueia release até correção ou aceitação explícita.

O threat model canônico está em `docs/security/threat-model.md`.

