# ADR-0004 — Distribuição FFmpeg para Windows x64

- **Status:** proposto; aguarda aprovação do owner
- **Data da investigação:** 2026-07-31
- **Decisor:** `caleo-hub`

## Necessidade

O aplicativo precisa de `ffprobe.exe` e `ffmpeg.exe` para analisar MP4/MP3/WAV e extrair apenas
áudio MP3. A aquisição deve ser reproduzível, compatível com Windows 10 x64 e verificável antes
do empacotamento. O aplicativo não baixará FFmpeg em runtime.

## Opções comparadas

| Critério | BtbN LGPL estático | Gyan release essentials |
|---|---|---|
| Referência no site do FFmpeg | linkado como build Windows | linkado como build Windows |
| Versão observada | `n8.1.2-34-g9b6c8969e0` | `8.1.2` |
| Artefato | `ffmpeg-n8.1.2-34-g9b6c8969e0-win64-lgpl-8.1.zip` | `ffmpeg-release-essentials.zip` |
| Tamanho observado | 145.349.121 bytes | 109.728.040 bytes |
| Licença do build | LGPL-3.0-or-later (`--enable-version3`, sem `--enable-gpl`) | GPL-3.0 |
| Forma | executáveis estáticos | executáveis estáticos |
| Windows mínimo declarado | Windows 10 22H2 | Windows 10 |
| URL | tag imutável no GitHub | alias de release que muda quando a versão muda |
| SHA-256 observado | `089e4169e93b2b3f3acbfced3c0704d24276a225641bdda04d796d28b07a2a38` | `db580001caa24ac104c8cb856cd113a87b0a443f7bdf47d8c12b1d740584a2ec` |

Ambas incluem `ffmpeg` e `ffprobe` e cobrem demux/decodificação de MP4, MP3 e WAV. A variante
LGPL da BtbN omite bibliotecas exclusivas GPL, como `libx264` e `libx265`; isso não impede a
decodificação nativa necessária nem a codificação MP3 por `libmp3lame` usada na extração.

## Recomendação

Adotar o **BtbN FFmpeg 8.1 LGPL estático**, fixado na tag
`autobuild-2026-07-31-14-10`, porque:

1. a URL, o nome completo e o SHA-256 identificam um artefato imutável;
2. os executáveis estáticos simplificam o pacote `onedir`;
3. a variante evita componentes GPL desnecessários para a primeira fatia;
4. o repositório de build documenta scripts, revisões de dependências e configuração;
5. Windows 10 22H2 está dentro do baseline aprovado do produto.

O script `scripts/fetch-ffmpeg.ps1` baixa apenas em `vendor/ffmpeg/bin/`, valida tamanho, SHA-256
e presença de `ffmpeg.exe`/`ffprobe.exe` antes de permitir extração. O diretório é ignorado pelo
Git; o ZIP e os binários não serão versionados.

## Obrigações propostas para distribuição

- incluir LGPL v3, avisos do FFmpeg/BtbN, configuração do build e `THIRD_PARTY.md` no instalador;
- disponibilizar link para o código-fonte correspondente e scripts de build;
- manter FFmpeg como processo separado, sem ligação das bibliotecas ao código Python;
- publicar o hash do pacote final e registrar o hash do ZIP de origem na evidência da release;
- revisar codecs e licença a cada atualização, sem seguir automaticamente o alias `latest`.

Este registro é evidência de engenharia, não aconselhamento jurídico.

## Atualização e rollback

Atualizações exigem nova tag imutável, novo hash, auditoria de configuração/licença e smoke de
MP4/MP3/WAV. Rollback restaura a versão anterior fixada e não altera chave ou saídas do usuário.

## Gate humano

Antes de extrair, executar, incorporar ou distribuir o binário, o owner deve aprovar
explicitamente esta versão, a origem BtbN e a licença LGPL-3.0-or-later.
