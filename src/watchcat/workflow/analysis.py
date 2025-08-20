from __future__ import annotations

from typing import Dict, List


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
