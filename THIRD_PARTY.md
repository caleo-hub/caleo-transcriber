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

Nenhum binário foi incorporado nesta fase. A origem, versão, configuração de codecs, checksum e obrigações LGPL/GPL do build escolhido devem ser registradas e verificadas antes de vendorização ou release. O aplicativo não pode baixar um binário arbitrário em runtime.

Este inventário é evidência de engenharia, não aconselhamento jurídico. A release precisa incluir avisos, fontes/ofertas ou demais materiais exigidos pelas licenças efetivamente escolhidas.

