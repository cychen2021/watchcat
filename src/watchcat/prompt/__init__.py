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

    # find all placeholders of the form ?<NAME>? or ?<NAME: fmt>? where
    # NAME can contain any char except '?' and fmt is an optional format
    # indicator such as 'json' or 'text'. If fmt is missing or empty default to 'text'.
    # Examples matched: ?<TOPICS>?, ?<TOPICS: json>?, ?<SUMMARY: text>?, ?<PH:>?
    # Match closing literal '?' as well so placeholders like ?<NAME>? are
    # fully consumed by the regex.
    pattern = re.compile(r"\?<([^?:>]+)(?:\s*:\s*([^>]*))?\>?\?")

    def _render(match: re.Match) -> str:
        name = match.group(1)
        fmt = match.group(2)
        # normalize format and default to 'text' when missing or blank
        if fmt is None:
            fmt = "text"
        else:
            fmt = fmt.strip().lower() if fmt.strip() != "" else "text"

        if name not in kwargs:
            raise KeyError(f"Placeholder '{name}' not provided")

        val = kwargs[name]

        if fmt == "json":
            # For json format always encode using compact JSON
            return json.dumps(val, ensure_ascii=False)
        elif fmt == "text":
            # For text format, keep strings as-is. For non-strings encode as
            # compact JSON so structures (lists/dicts) are preserved with
            # consistent, machine-friendly representation.
            if isinstance(val, str):
                return val
            return json.dumps(val, ensure_ascii=False)
        else:
            # Unknown format indicator — be strict and raise an error so
            # templates don't silently behave unexpectedly.
            raise ValueError(f"Unknown placeholder format '{fmt}' for '{name}'")

    return pattern.sub(_render, template)
