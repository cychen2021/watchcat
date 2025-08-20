import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional


class Database:
    """A minimal sqlite-backed Database for storing workflow items.

    Tables created: topics, summaries, analyses, evaluations.

    Each table has at least: id TEXT PRIMARY KEY and timestamp TEXT (ISO-8601).
    """

    SCHEMA = {
        "topics": (
            "id TEXT PRIMARY KEY",
            "description TEXT",
            "timestamp TEXT",
        ),
        "summaries": (
            "id TEXT PRIMARY KEY",
            "summary TEXT",
            "original_content TEXT",
            "keywords TEXT",
            "category_of_the_source TEXT",
            "timestamp TEXT",
        ),
        "analyses": (
            "id TEXT PRIMARY KEY",
            "related_topics TEXT",
            "envisaged_interaction TEXT",
            "timestamp TEXT",
        ),
        "evaluations": (
            "id TEXT PRIMARY KEY",
            "relevance TEXT",
            "feasibility TEXT",
            "importance TEXT",
            "timestamp TEXT",
        ),
    }

    def __init__(self, db_path: str = ":memory:") -> None:
        """Open (or create) the sqlite database and ensure schema exists.

        Args:
            db_path: path to sqlite file or ":memory:" for ephemeral DB.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cur = self.conn.cursor()
        for table, columns in self.SCHEMA.items():
            cols = ", ".join(columns)
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({cols})")
        self.conn.commit()

    def close(self) -> None:
        """Close the underlying connection."""
        try:
            self.conn.close()
        except Exception:
            pass

    # --- topic ---
    def store_topic(self, id: str, description: str, timestamp: Optional[str]) -> None:
        """Store or replace a Topic row.

        Args:
            id: topic id
            description: topic description
            timestamp: ISO timestamp or None to use current UTC time
        """
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO topics (id, description, timestamp) VALUES (?, ?, ?)",
            (id, description, ts),
        )
        self.conn.commit()

    def get_topics(self) -> Iterable[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, description, timestamp FROM topics")
        for row in cur.fetchall():
            yield dict(row)

    # --- summary ---
    def store_summary(
        self,
        id: str,
        summary: str,
        original_content: str,
        keywords: str,
        category_of_the_source: str,
        timestamp: Optional[str],
    ) -> None:
        """Store or replace a Summary row.

        Note: `keywords` is expected as a comma-separated string.
        """
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO summaries (id, summary, original_content, keywords, category_of_the_source, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (id, summary, original_content, keywords, category_of_the_source, ts),
        )
        self.conn.commit()

    def get_summaries(self) -> Iterable[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, summary, original_content, keywords, category_of_the_source, timestamp FROM summaries"
        )
        for row in cur.fetchall():
            yield dict(row)

    # --- analysis ---
    def store_analysis(
        self,
        id: str,
        related_topics: str,
        envisaged_interaction: str,
        timestamp: Optional[str],
    ) -> None:
        """Store or replace an Analysis row.

        Note: `related_topics` is expected as a comma-separated string of topic ids.
        """
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO analyses (id, related_topics, envisaged_interaction, timestamp) VALUES (?, ?, ?, ?)",
            (id, related_topics, envisaged_interaction, ts),
        )
        self.conn.commit()

    def get_analyses(self) -> Iterable[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, related_topics, envisaged_interaction, timestamp FROM analyses"
        )
        for row in cur.fetchall():
            yield dict(row)

    # --- evaluation ---
    def store_evaluation(
        self,
        id: str,
        relevance: str,
        feasibility: str,
        importance: str,
        timestamp: Optional[str],
    ) -> None:
        """Store or replace an Evaluation row."""
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO evaluations (id, relevance, feasibility, importance, timestamp) VALUES (?, ?, ?, ?, ?)",
            (id, relevance, feasibility, importance, ts),
        )
        self.conn.commit()

    def get_evaluations(self) -> Iterable[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, relevance, feasibility, importance, timestamp FROM evaluations"
        )
        for row in cur.fetchall():
            yield dict(row)
