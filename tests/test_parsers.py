import json
from watchcat.workflow.summary import Summary
from watchcat.workflow.analysis import Analysis
from watchcat.workflow.evaluation import Evaluation


def test_summary_parse_with_fenced_json():
    text = """Some explanation text

```json
{
  "summary": "Short summary",
  "original_content": "Full content...",
  "keywords": ["key1", "key2"],
  "category_of_the_source": "research"
}
```
"""
    obj = Summary.parse(text)
    assert obj["summary"] == "Short summary"
    assert obj["category_of_the_source"] == "research"


def test_analysis_parse_raw_json_with_extra_text():
    text = "Analysis results:\n" + json.dumps(
        {"related_topics": ["topic1", "topic2"], "envisaged_interaction": "It may help"}
    )
    obj = Analysis.parse(text)
    assert "related_topics" in obj
    assert obj["related_topics"][0] == "topic1"


def test_evaluation_parse_and_validate():
    text = 'Answer:\n```json\n{\n  "relevance": "high",\n  "feasibility": "medium",\n  "importance": "low"\n}\n```'
    obj = Evaluation.parse(text)
    assert obj["relevance"] == "high"


def test_evaluation_invalid_rating_raises():
    text = '{"relevance": "super", "feasibility": "low", "importance": "high"}'
    try:
        Evaluation.parse(text)
        assert False, "Expected ValueError for invalid rating"
    except ValueError:
        pass
