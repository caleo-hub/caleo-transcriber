# Dependências de terceiros

Inventário inicial obtido dos metadados dos pacotes instalados em 2026-07-31. O lock exato está em `pyproject.toml`; dependências transitivas são auditadas no harness e receberão SBOM antes da release.

| Componente | Versão | Licença declarada | Uso |
|---|---:|---|---|
| PySide6 | 6.11.1 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | UI Qt |
| OpenAI SDK | 2.52.0 | Apache-2.0 | adapter cloud |
| keyring | 25.7.0 | MIT | Windows Credential Manager |
| PyInstaller | 6.21.0 | GPL-2.0-or-later com exceção para empacotar programas não livres | build Windows |
| Ruff | 0.16.1 | MIT | lint/format |
| mypy | 2.3.0 | MIT | tipos |
| pytest | 9.1.1 | MIT | testes |

## FFmpeg

O build aprovado pelo owner em 2026-07-31 é o estático Windows x64 LGPL da BtbN:

- FFmpeg `8.1.2-34-g9b6c8969e0`;
- tag imutável `autobuild-2026-07-31-14-10`;
- variante `win64-lgpl-8.1`, licenciada como LGPL-3.0-or-later;
- SHA-256 `089e4169e93b2b3f3acbfced3c0704d24276a225641bdda04d796d28b07a2a38`;
- origem e comparação: `docs/adr/ADR-0004-distribuicao-ffmpeg-windows.md`;
- aquisição verificável: `scripts/fetch-ffmpeg.ps1`.

O aplicativo não baixa FFmpeg em runtime. O ZIP permanece fora do Git; o pipeline de pacote deve
adquiri-lo pelo script fixado, verificar o hash e incluir os avisos e fontes correspondentes.

Este inventário é evidência de engenharia, não aconselhamento jurídico. A release precisa incluir avisos, fontes/ofertas ou demais materiais exigidos pelas licenças efetivamente escolhidas.
