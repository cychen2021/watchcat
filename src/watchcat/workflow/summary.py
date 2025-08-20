from __future__ import annotations
from typing import Dict, List


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

    def build(self, summary: str, original_content: str, keywords: List[str], category: str) -> Dict[str, object]:
        """Create a summary item using the instance id.

        Args and returns: same as before, but the `id` is taken from
        the instance `__init__` argument.
        """
        return {
            "summary": summary,
            "original_content": original_content,
            "keywords": keywords,
            "category_of_the_source": category,
            "id": self.id,
        }
