# Threat model proporcional — primeira fatia

- **Status:** controles e risco residual aceitos pelo owner em 2026-07-31
- **Data:** 2026-07-31
- **Método:** fronteiras de confiança + STRIDE adaptado

## Ativos

1. chave da OpenAI;
2. áudio/vídeo pessoal e transcrição;
3. arquivos preexistentes do usuário;
4. integridade do executável e dependências;
5. controle de custo da API.

## Fronteiras de confiança

- usuário ↔ aplicativo;
- aplicativo ↔ filesystem/temporários;
- aplicativo ↔ Windows Credential Manager;
- aplicativo ↔ processo FFmpeg;
- aplicativo ↔ OpenAI via HTTPS;
- pipeline de build ↔ artefato distribuído.

## Ameaças e controles

| ID | Ameaça | Controle obrigatório | Evidência | Residual |
|---|---|---|---|---|
| T-01 | chave em configuração/log/pacote | Credential Manager, mascaramento, zero logs de headers, secret scan | teste e inspeção do pacote | malware no mesmo usuário pode acessar recursos do usuário |
| T-02 | vídeo enviado por engano | adapter recebe somente `PreparedAudio`; teste inspeciona multipart | teste de contrato | falha do extrator/dependência |
| T-03 | mídia/texto em temporário abandonado | diretório privado por tentativa, cleanup em `finally` e no startup | teste de crash/cleanup | encerramento e acesso local antes da limpeza |
| T-04 | sobrescrita ou path traversal | destino escolhido, nome sanitizado, criação exclusiva e replace atômico | testes de colisão/Unicode/path | outro processo local pode disputar arquivos |
| T-05 | injeção via nome de arquivo no FFmpeg | argumentos em lista, `shell=False`, marcador `--` quando suportado | teste com metacaracteres | vulnerabilidade no decoder |
| T-06 | mídia malformada explora FFmpeg | versão travada, input não confiável, timeout, processo com privilégios do usuário | SCA + corpus negativo | zero-day no decoder |
| T-07 | custo duplicado por retry | sem retry automático após upload; ação manual visível | teste de política | usuário pode repetir manualmente |
| T-08 | supply-chain/artefato adulterado | lock com hashes, SBOM, licenças, CI, checksums de release | pipeline e artefatos | conta/repositório comprometido |
| T-09 | endpoint falso/MITM | SDK oficial, TLS verificado, endpoint fixo, sem proxy customizado na UI | teste de configuração | confiança no SO/CA e dependências |
| T-10 | conteúdo sensível em erro bruto | mapper para códigos e mensagens próprias; conteúdo nunca no logger | teste com canários | crash dump externo ao app |

## Dados e retenção

- sem conta, autorização multiusuário, banco, analytics ou histórico;
- chave persiste somente no cofre do Windows;
- preferências não secretas podem persistir localmente;
- mídia preparada e resultado intermediário são efêmeros;
- TXT final existe apenas no destino escolhido;
- OpenAI recebe somente áudio após ação explícita no modo cloud.

## Risco residual aceito

Mesmo com os controles, a OpenAI processará o áudio enviado, malware executado na mesma conta Windows pode acessar dados do usuário, e decoders de mídia possuem risco de vulnerabilidades. Em 2026-07-31, `caleo-hub` aceitou esse residual como proporcional ao uso pessoal.
