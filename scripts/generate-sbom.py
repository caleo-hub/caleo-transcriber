"""Gera SBOM SPDX do fechamento transitivo de dependências de runtime."""

import argparse
import json
import re
import shutil
from importlib import metadata
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOTS = ("keyring", "openai", "PySide6")


def _spdx_id(name: str) -> str:
    return "SPDXRef-Package-" + re.sub(r"[^A-Za-z0-9.-]", "-", name)


def _runtime_closure() -> dict[str, metadata.Distribution]:
    pending = list(ROOTS)
    found: dict[str, metadata.Distribution] = {}
    while pending:
        requested = pending.pop()
        canonical = canonicalize_name(requested)
        if canonical in found:
            continue
        distribution = metadata.distribution(requested)
        found[canonical] = distribution
        for raw_requirement in distribution.requires or ():
            requirement = Requirement(raw_requirement)
            if requirement.marker is not None and not requirement.marker.evaluate({"extra": ""}):
                continue
            pending.append(requirement.name)
    return found


def _copy_licenses(distributions: dict[str, metadata.Distribution], destination: Path) -> None:
    for canonical, distribution in sorted(distributions.items()):
        for relative in distribution.files or ():
            parts = [part.lower() for part in relative.parts]
            if "licenses" not in parts:
                continue
            source = Path(str(distribution.locate_file(relative)))
            if not source.is_file():
                continue
            target = destination / canonical / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--created", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--licenses-dir", required=True, type=Path)
    arguments = parser.parse_args()

    distributions = _runtime_closure()
    packages: list[dict[str, object]] = [
        {
            "SPDXID": "SPDXRef-Package-CaleoTranscriber",
            "name": "caleo-transcriber",
            "versionInfo": arguments.version,
            "downloadLocation": "https://github.com/caleo-hub/caleo-transcriber",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "LicenseRef-Proprietary",
            "supplier": "Organization: caleo-hub",
        }
    ]
    relationships: list[dict[str, str]] = [
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relationshipType": "DESCRIBES",
            "relatedSpdxElement": "SPDXRef-Package-CaleoTranscriber",
        }
    ]
    root_names = {canonicalize_name(name) for name in ROOTS}
    for canonical, distribution in sorted(distributions.items()):
        name = distribution.metadata["Name"] or canonical
        package_id = _spdx_id(canonical)
        license_expression = distribution.metadata.get("License-Expression") or "NOASSERTION"
        packages.append(
            {
                "SPDXID": package_id,
                "name": name,
                "versionInfo": distribution.version,
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": license_expression,
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": f"pkg:pypi/{canonical}@{distribution.version}",
                    }
                ],
            }
        )
        if canonical in root_names:
            relationships.append(
                {
                    "spdxElementId": "SPDXRef-Package-CaleoTranscriber",
                    "relationshipType": "DEPENDS_ON",
                    "relatedSpdxElement": package_id,
                }
            )

    document = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"Caleo Transcriber {arguments.version}",
        "documentNamespace": (
            "https://github.com/caleo-hub/caleo-transcriber/sbom/"
            f"{arguments.version}/{arguments.commit}"
        ),
        "creationInfo": {
            "created": arguments.created,
            "creators": ["Tool: caleo-transcriber/scripts/generate-sbom.py"],
        },
        "packages": packages,
        "relationships": relationships,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _copy_licenses(distributions, arguments.licenses_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
