from __future__ import annotations
from typing import Dict, List
import json
import re
from typing import Any


class Summary:
    """Build summary items for the workflow.

    The caller must provide an `id` when instantiating the builder. The
    `build` method will include this id on generated items.

    Usage:
        s = Summary(id="custom-id-1")
        item = s.build("short summary", "orig...", ["key1"], "research")
    """

    def __init__(self, id: str) -> None:
        self.id = id

    def build(
        self, summary: str, source_id: str, keywords: List[str], category: str
    ) -> Dict[str, object]:
        """Create a summary item using the instance id.

        Args and returns: same as before, but the `id` is taken from
        the instance `__init__` argument.
        """
        return {
            "summary": summary,
            "source_id": source_id,
            "keywords": keywords,
            "category_of_the_source": category,
            "id": self.id,
        }

    @classmethod
    def parse(cls, text: str) -> Dict[str, Any]:
        """Parse an LLM response text and return the expected summary dict.

        The LLM may return a fenced code block with ```json ... ``` or raw JSON.
        This helper extracts the JSON payload and returns it as a dict.
        """
        if text is None:
            raise ValueError("No text to parse")

        # Try to find a ```json ...``` block first
        m = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
        json_text = None
        if m:
            json_text = m.group(1)
        else:
            # Fallback: try to find any JSON object in the text
            m2 = re.search(r"(\{(?:.|\n)*\})", text, flags=re.S)
            if m2:
                json_text = m2.group(1)

        if not json_text:
            raise ValueError("No JSON object found in text")

        obj = json.loads(json_text)

        # Basic shape validation
        for key in (
            "summary",
            "source_id",
            "keywords",
            "category_of_the_source",
        ):
            if key not in obj:
                raise ValueError(f"Missing key in summary JSON: {key}")

        return obj
