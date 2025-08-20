from pathlib import Path


def _load_db():
    # Load the datastore Database class by running its __init__.py directly
    mod_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "watchcat"
        / "datastore"
        / "__init__.py"
    )
    import runpy

    return runpy.run_path(str(mod_path))["Database"]


def test_database_store_and_get_roundtrip():
    Database = _load_db()

    db = Database(db_path=":memory:")

    # topics
    db.store_topic("t1", "A topic", None)
    topics = list(db.get_topics())
    assert any(t["id"] == "t1" and t["description"] == "A topic" for t in topics)

    # summaries
    db.store_summary("s1", "sum", "orig", "k1,k2", "mail", None)
    summaries = list(db.get_summaries())
    assert any(s["id"] == "s1" and s["summary"] == "sum" for s in summaries)

    # analyses
    db.store_analysis("a1", "t1", "interaction", None)
    analyses = list(db.get_analyses())
    assert any(
        a["id"] == "a1" and "interaction" in a["envisaged_interaction"]
        for a in analyses
    )

    # evaluations
    db.store_evaluation("e1", "rel", "feas", "imp", None)
    evals = list(db.get_evaluations())
    assert any(e["id"] == "e1" and e["relevance"] == "rel" for e in evals)

    db.close()
