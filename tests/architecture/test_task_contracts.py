from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[2]
TASKS_ROOT = PROJECT_ROOT / "docs" / "tasks"
REQUIRED_HEADINGS = {
    "## Objetivo",
    "## Contexto e fontes",
    "## Escopo de arquivos",
    "## Restrições e autonomia",
    "## Critérios de aceitação",
    "## Validação e evidência",
    "## Rollback",
}


@pytest.mark.architecture
def test_increment_plans_have_nineteen_bounded_task_contracts() -> None:
    tasks = sorted(TASKS_ROOT.glob("TASK-*.md"))
    assert [path.name[:8] for path in tasks] == [f"TASK-{number:03d}" for number in range(1, 20)]


@pytest.mark.architecture
@pytest.mark.parametrize("task", sorted(TASKS_ROOT.glob("TASK-*.md")))
def test_every_task_contract_has_operational_sections(task: Path) -> None:
    text = task.read_text(encoding="utf-8")
    missing = REQUIRED_HEADINGS - set(text.splitlines())
    assert missing == set(), f"{task.name}: seções ausentes {sorted(missing)}"


@pytest.mark.architecture
def test_pilot_explicitly_forbids_secrets_and_network() -> None:
    pilot = (TASKS_ROOT / "TASK-001-credential-store-port.md").read_text(encoding="utf-8")
    assert "Não usar `keyring`, ambiente, filesystem, logs, rede ou secrets" in pilot
    assert "`verify.cmd`" in pilot
