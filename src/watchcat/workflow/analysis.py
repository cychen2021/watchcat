from __future__ import annotations

from typing import Dict, List
import json
import re
from typing import Any


class Analysis:
    """Build analysis items for the workflow using a caller-provided id.

    Usage:
        a = Analysis(id="analysis-1")
        item = a.build(["topic1"], "interaction text")
    """

    def __init__(self, id: str) -> None:
        self.id = id

    def build(
        self, related_topics: List[str], envisaged_interaction: str
    ) -> Dict[str, object]:
        """Create an analysis item using the instance id.

        Args and returns: same as before, but the `id` is taken from
        the instance `__init__` argument.
        """
        return {
            "related_topics": related_topics,
            "envisaged_interaction": envisaged_interaction,
            "id": self.id,
        }

    @classmethod
    def parse(cls, text: str) -> Dict[str, Any]:
        """Parse LLM response text and return the analysis dict.

        Accepts responses containing a ```json ... ``` fenced block or raw JSON.
        """
        if text is None:
            raise ValueError("No text to parse")

        m = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
        json_text = None
        if m:
            json_text = m.group(1)
        else:
            m2 = re.search(r"(\{(?:.|\n)*\})", text, flags=re.S)
            if m2:
                json_text = m2.group(1)

        if not json_text:
            raise ValueError("No JSON object found in text")

        obj = json.loads(json_text)

        if "related_topics" not in obj or "envisaged_interaction" not in obj:
            raise ValueError("Missing keys in analysis JSON")

        return obj
