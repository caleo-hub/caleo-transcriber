# Validação da TASK-010 — candidato 0.1.0

- **Estado:** candidato local validado; release bloqueada
- **Data:** 2026-07-31
- **Plataforma de build:** Windows x64 do owner, não uma VM Windows 10 limpa

## Evidência automatizada disponível

- PyInstaller `onedir` contém o aplicativo, runtime, Qt, Credential Manager e FFmpeg/ffprobe;
- inspeção confirma executável PE x64, arquivos obrigatórios e ausência dos padrões proibidos;
- smoke abre o executável empacotado sem Python externo e encerra com sucesso;
- SBOM SPDX, inventário de licenças, notas e SHA-256 são gerados;
- Inno Setup 6.7.3 produz um instalador x64 único;
- preflight valida o conjunto do candidato;
- ensaio reversível retira e restaura o candidato não publicado preservando seu digest.

Os valores exatos de commit, digest, tamanhos e tempos ficam em `build-evidence.json`, produzido
junto ao candidato e novamente gerado pelo workflow de pacote. O diretório local do candidato é
ignorado pelo Git.

## Gate ainda não satisfeito

- instalar e desinstalar o candidato não foi autorizado nem executado;
- o smoke não ocorreu em uma VM Windows 10 x64 limpa;
- nenhuma mídia ou chave real foi usada e nenhuma chamada paga à OpenAI foi feita;
- o instalador não possui assinatura Authenticode;
- o owner ainda não aprovou este artefato para publicação;
- nenhuma GitHub Release foi criada.

Essas lacunas não invalidam o build técnico da TASK-010, mas impedem promover o candidato a release.

## Rollback observado

O build mede a retirada e restauração do candidato ainda não publicado, conferindo o SHA-256 antes
e depois. O ensaio completo de desinstalação e preservação de dados permanece no gate de Windows 10
limpo.
