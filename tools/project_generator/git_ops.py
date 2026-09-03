"""Optional Git repository initialization."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def init_repository(destination: Path, *, branch: str = "main") -> bool:
    """Initialize a Git repository if Git is available and the directory is not a repo."""
    if shutil.which("git") is None or (destination / ".git").exists():
        return False
    subprocess.run(["git", "init", "-b", branch], cwd=destination, check=True)
    return True
