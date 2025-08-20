from __future__ import annotations

from typing import Dict


class Evaluation:
    """Build evaluation items for the workflow using a caller-provided id.

    Usage:
        e = Evaluation(id="eval-1")
        item = e.build("high", "medium", "low")
    """

    VALID_RATINGS = {"high", "medium", "low"}

    def __init__(self, id: str) -> None:
        self.id = id

    def build(self, relevance: str, feasibility: str, importance: str) -> Dict[str, object]:
        """Create an evaluation item using the instance id; validate ratings.

        Raises ValueError if any rating is invalid.
        """
        for name, val in (("relevance", relevance), ("feasibility", feasibility), ("importance", importance)):
            if val not in self.VALID_RATINGS:
                raise ValueError(f"{name} must be one of {sorted(self.VALID_RATINGS)}, got: {val}")

        return {
            "relevance": relevance,
            "feasibility": feasibility,
            "importance": importance,
            "id": self.id,
        }
