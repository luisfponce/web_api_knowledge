"""Strict Jinja2 rendering for project templates."""

from __future__ import annotations

import shutil
import tempfile
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .errors import RenderError
from .manifest import TemplateSpec, build_manifest
from .models import ProjectConfig
from .validators import validate_config


TEMPLATE_ROOT = Path(__file__).parent / "templates"


def create_environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_ROOT),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["toml_bool"] = lambda value: "true" if value else "false"
    env.filters["json_string"] = lambda value: json.dumps(str(value))
    env.filters["js_string"] = lambda value: json.dumps(str(value))
    env.filters["py_string"] = lambda value: json.dumps(str(value))
    env.filters["toml_string"] = lambda value: json.dumps(str(value))
    return env


def render_project(config: ProjectConfig) -> list[Path]:
    """Render a project to its destination and return written file paths."""
    validate_config(config, allow_existing_empty=False)
    manifest = build_manifest(config)
    env = create_environment()

    destination = config.destination
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"{config.slug}-", dir=destination.parent) as temp_name:
        temp_dir = Path(temp_name)
        written = _render_manifest(env, config, manifest, temp_dir)
        if destination.exists():
            if any(destination.iterdir()):
                raise RenderError(f"Destination became non-empty during render: {destination}")
        else:
            destination.mkdir(parents=True)
        for path in temp_dir.rglob("*"):
            if path.is_dir():
                continue
            relative = path.relative_to(temp_dir)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), target)
        return [destination / path for path in written]


def render_to_directory(config: ProjectConfig, output_dir: Path) -> list[Path]:
    """Render into an already controlled directory, useful for tests."""
    validate_config(config, allow_existing_empty=True)
    env = create_environment()
    return [output_dir / path for path in _render_manifest(env, config, build_manifest(config), output_dir)]


def _render_manifest(
    env: Environment,
    config: ProjectConfig,
    manifest: list[TemplateSpec],
    output_dir: Path,
) -> list[Path]:
    context = {"config": config, "services": config.generated_services}
    written: list[Path] = []
    for spec in manifest:
        template = env.get_template(spec.template)
        relative_path = Path(spec.destination)
        target = output_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(template.render(context), encoding="utf-8")
        written.append(relative_path)
    return written
