# Validação da TASK-022

- PR: #17, checks `verify`, `gitleaks` e `package` aprovados.
- Commit da release: `1b01f3d9948372816146555bc36487406c501664`.
- Tag: `v0.2.1-beta.1`, prerelease pública e não draft.
- Assets: instalador, checksum, SBOM, licenças, notas e evidência de build.
- Instalador: `CaleoTranscriber-Setup-0.2.1-x64.exe`, 114.174.021 bytes.
- SHA-256: `c079f478cf5833d6c7ac589f16c789aaf3ed80c38035289a6c89e6ec095f99a6`.
- Preflight pós-download: aprovado sem executar ou instalar o aplicativo.
- Build: x64, smoke do pacote aprovado, sem Authenticode.
- OpenAI: tentativa anterior com áudio sintético retornou `OPENAI_401`; a chave recusada não foi
  empacotada e precisa ser substituída pela UI.
- Privacidade: o vídeo pessoal não foi enviado e nenhuma transcrição foi registrada.
- Rollback: `v0.2.0-beta.1` permanece publicada.
