from __future__ import annotations

from typing import Dict
import json
import re
from typing import Any


class Evaluation:
    """Build evaluation items for the workflow using a caller-provided id.

    Usage:
        e = Evaluation(id="eval-1")
        item = e.build("high", "medium", "low")
    """

    VALID_RATINGS = {"high", "medium", "low"}

    def __init__(self, id: str) -> None:
        self.id = id

    def build(
        self, relevance: str, feasibility: str, importance: str
    ) -> Dict[str, object]:
        """Create an evaluation item using the instance id; validate ratings.

        Raises ValueError if any rating is invalid.
        """
        for name, val in (
            ("relevance", relevance),
            ("feasibility", feasibility),
            ("importance", importance),
        ):
            if val not in self.VALID_RATINGS:
                raise ValueError(
                    f"{name} must be one of {sorted(self.VALID_RATINGS)}, got: {val}"
                )

        return {
            "relevance": relevance,
            "feasibility": feasibility,
            "importance": importance,
            "id": self.id,
        }

    @classmethod
    def parse(cls, text: str) -> Dict[str, Any]:
        """Parse LLM response text and return the evaluation dict.

        Extract JSON from fenced code block or raw JSON and validate ratings.
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

        for key in ("relevance", "feasibility", "importance"):
            if key not in obj:
                raise ValueError(f"Missing key in evaluation JSON: {key}")
            if obj[key] not in cls.VALID_RATINGS:
                raise ValueError(f"Invalid rating for {key}: {obj[key]}")

        return obj
