"""Load prompt templates shipped with the package.

Templates live next to this module as markdown files and are named
`<name>.prompt.md` (for example: `analyze.prompt.md`).

This helper accepts `name` with or without the `.prompt.md` suffix and
returns the file content as a string. If the requested template does not
exist a FileNotFoundError is raised and the list of available templates
is included in the message.
"""

from pathlib import Path
from typing import List

_THIS_DIR = Path(__file__).resolve().parent
_TEMPLATE_SUFFIX = ".prompt.md"


def _available_templates() -> List[str]:
    return [p.name for p in _THIS_DIR.glob(f"*{_TEMPLATE_SUFFIX}") if p.is_file()]


def load_prompt_template(name: str) -> str:
    if not name:
        raise ValueError("template name must be a non-empty string")

    # accept names like 'analyze' or 'analyze.prompt.md'
    if name.endswith(_TEMPLATE_SUFFIX):
        filename = name
    else:
        filename = f"{name}{_TEMPLATE_SUFFIX}"

    path = _THIS_DIR / filename
    if not path.exists() or not path.is_file():
        available = _available_templates()
        raise FileNotFoundError(
            f"Prompt template '{name}' not found. Expected file '{filename}'."
            f" Available templates: {available}"
        )

    return path.read_text(encoding="utf-8")
