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

def fill_out(template: str, **kwargs) -> str:
    """Fill out a prompt template by substituting placeholders.

    Placeholders use the pattern `?<NAME>?` (for example `?<TOPICS>?`).

    Rules:
    - If a placeholder's value in ``kwargs`` is a string, it is inserted as-is.
    - If the value is not a string, it is JSON-encoded (compact) before
      insertion so structures (lists/dicts) are preserved.
    - If the template contains a placeholder for which no kwarg was
      provided a KeyError is raised naming the missing placeholder.

    Args:
        template: The template string containing zero or more placeholders.
        **kwargs: Mapping of placeholder names to values to insert.

    Returns:
        The template with placeholders substituted.

    Raises:
        KeyError: If a placeholder in the template has no corresponding
            value in ``kwargs``.
    """
    import re
    import json

    if template is None:
        raise ValueError("template must be a non-empty string")

    # find all placeholders of the form ?<NAME>? where NAME can contain
    # letters, numbers, underscores, hyphens and slashes (to allow json-like
    # keys used in some templates). We will be permissive and capture any
    # sequence of characters that is not a question mark.
    pattern = re.compile(r"\?<([^?]+)\>\?")

    def _render(match: re.Match) -> str:
        key = match.group(1)
        if key not in kwargs:
            raise KeyError(f"Placeholder '{key}' not provided")
        val = kwargs[key]
        if isinstance(val, str):
            return val
        # JSON-encode non-strings in a compact form
        return json.dumps(val, ensure_ascii=False)

    return pattern.sub(_render, template)
