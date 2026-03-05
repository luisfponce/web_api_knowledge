import subprocess
import sys
from pathlib import Path


def test_run_functional_suite():
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/functional", "-v"],
        cwd=project_root,
        check=False,
    )
    assert result.returncode == 0
