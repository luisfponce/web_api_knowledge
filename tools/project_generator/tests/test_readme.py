from pathlib import Path


def test_readme_documents_install_usage_config_and_validation() -> None:
    readme = Path("tools/project_generator/README.md").read_text(encoding="utf-8")

    assert "python -m pip install -r tools/project_generator/requirements.txt" in readme
    assert "python -m tools.project_generator" in readme
    assert "--config tools/project_generator/config.yaml" in readme
    assert "CLI Reference" in readme
    assert "Validation And Safety" in readme
    assert "config.local.yaml" in readme
    assert "Multiple top-level packages discovered" in readme
    assert "npm ci" in readme
