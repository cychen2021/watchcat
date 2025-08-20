from collections.abc import Collection, Sequence
from google import genai
from google.genai import types

from ..datastore import Database
from ..prompt import fill_out_prompt, load_prompt_template
from ..puller import Mailbox, Post, Source, SourceKind
from .analysis import Analysis
from .evaluation import Evaluation
from .summary import Summary
import json
import re
from typing import Any, Dict


class Workflow:
    """Main workflow for processing posts from multiple sources."""

    def __init__(self, sources: Collection[Source]) -> None:
        """Initialize the workflow with a collection of sources.

        Args:
            sources: Collection of sources to pull posts from
        """
        self.sources = sources
        self.database = Database()

    def run(self) -> None:
        """Execute the complete workflow pipeline.

        This method performs the following steps:
        1. Pull posts from all sources (currently focusing on Mailbox sources)
        2. Store pulled posts in the database
        3. Orchestrate posts into prompts
        4. Generate summaries using LLM
        5. Generate analyses of summaries
        6. Generate evaluations of analyses
        """
        # Pull posts from all sources.
        # Currently, we only consider `Mailbox` sources and don't apply any filter
        all_posts = self._pull_posts_from_sources()

        # Store the pulled posts in the database
        self._store_posts_in_database(all_posts)

        # Orchestrate the posts into a single prompt
        orchestrated_prompt = self._orchestrate_posts_to_prompt(all_posts)

        # Use the `summarize` prompt template for the LLM to generate the summaries
        # and store them in the database
        summaries = self._generate_summaries(orchestrated_prompt)
        self._store_summaries_in_database(summaries)

        # Use the `analyze` prompt template for the LLM to generate the analyses of the summaries
        # and store them in the database
        analyses = self._generate_analyses(summaries)
        self._store_analyses_in_database(analyses)

        # Use the `evaluate` prompt template for the LLM to generate the evaluations of the analyses
        # and store them in the database
        evaluations = self._generate_evaluations(analyses)
        self._store_evaluations_in_database(evaluations)

    def _pull_posts_from_sources(self) -> Sequence[Post]:
        """Pull posts from all configured sources.

        Currently focuses on Mailbox sources without applying filters.

        Returns:
            Sequence of all pulled posts
        """
        all_posts = []

        for source in self.sources:
            if isinstance(source, Mailbox) or source.kind == SourceKind.MAIL:
                # Pull from mailbox sources without filters
                posts = source.pull()
                all_posts.extend(posts)

        return all_posts

    def _store_posts_in_database(self, posts: Sequence[Post]) -> None:
        """Store pulled posts in the database.

        Args:
            posts: Sequence of posts to store
        """
        # TODO: Implement database storage for posts
        print(f"TODO: Store {len(posts)} posts in database")

    def _orchestrate_posts_to_prompt(self, posts: Sequence[Post]) -> str:
        """Orchestrate multiple posts into a single prompt.

        Args:
            posts: Sequence of posts to orchestrate

        Returns:
            Combined prompt string
        """
        if not posts:
            return ""

        prompt_parts = []
        prompt_parts.append("# Combined Posts for Analysis\n")

        for i, post in enumerate(posts, 1):
            prompt_parts.append(f"## Post {i}")
            prompt_parts.append(f"Source: {post.source}")
            prompt_parts.append(f"Published: {post.published_date}")
            prompt_parts.append(f"URL: {post.url}")
            prompt_parts.append("")
            prompt_parts.append(post.to_prompt())
            prompt_parts.append("")

        return "\n".join(prompt_parts)

    def _generate_summaries(self, orchestrated_prompt: str) -> Sequence[Summary]:
        """Generate summaries using the summarize prompt template.

        Args:
            orchestrated_prompt: The combined prompt from all posts

        Returns:
            Generated summaries
        """
        try:
            # Create GenAI client
            client = genai.Client()

            # Load the summarize prompt template
            summarize_template = load_prompt_template("summarize")

            # Fill out the prompt template with the orchestrated content
            full_prompt = fill_out_prompt(
                summarize_template, content=orchestrated_prompt
            )

            # Generate content using Google GenAI
            response = client.models.generate_content(
                model="gemini-2.0-flash-001", contents=full_prompt
            )

            # Extract text from the response in a tolerant way
            text = self._extract_text_from_response(response)

            # If Summary class provides a parse method, use it to obtain JSON and an id
            try:
                if hasattr(Summary, "parse"):
                    parsed = Summary.parse(text)
                    summary_id = parsed.get("id", "summary_1")
                    summary = Summary(id=summary_id)
                else:
                    summary = Summary(id="summary_1")

                return [summary]
            except Exception:
                # Parsing failed - return fallback placeholder
                placeholder_summary = Summary(id="placeholder_summary_1")
                return [placeholder_summary]

        except Exception as e:
            # Fallback for development/testing
            placeholder_summary = Summary(id="placeholder_summary_1")
            return [placeholder_summary]

    def _store_summaries_in_database(self, summaries: Sequence[Summary]) -> None:
        """Store generated summaries in the database.

        Args:
            summaries: Generated summaries to store
        """
        # TODO: Implement database storage for summaries
        print(f"TODO: Store {len(summaries)} summaries in database")

    def _generate_analyses(self, summaries: Sequence[Summary]) -> Sequence[Analysis]:
        """Generate analyses using the analyze prompt template.

        Args:
            summaries: The generated summaries to analyze

        Returns:
            Generated analyses
        """
        try:
            # Create GenAI client
            client = genai.Client()

            # Load the analyze prompt template
            analyze_template = load_prompt_template("analyze")

            # Combine summaries into analysis prompt
            summaries_text = "\n\n".join(
                [
                    f"Summary {i + 1}: {summary.build('temp_summary', 'temp_content', [], 'temp_category')}"
                    for i, summary in enumerate(summaries)
                ]
            )

            # Fill out the prompt template with the summaries
            full_prompt = fill_out_prompt(analyze_template, content=summaries_text)

            # Generate content using Google GenAI
            response = client.models.generate_content(
                model="gemini-2.0-flash-001", contents=full_prompt
            )

            text = self._extract_text_from_response(response)

            try:
                if hasattr(Analysis, "parse"):
                    parsed = Analysis.parse(text)
                    analysis_id = parsed.get("id", "analysis_1")
                    analysis = Analysis(id=analysis_id)
                else:
                    analysis = Analysis(id="analysis_1")

                return [analysis]
            except Exception:
                placeholder_analysis = Analysis(id="placeholder_analysis_1")
                return [placeholder_analysis]

        except Exception as e:
            # Fallback for development/testing
            placeholder_analysis = Analysis(id="placeholder_analysis_1")
            return [placeholder_analysis]

    def _store_analyses_in_database(self, analyses: Sequence[Analysis]) -> None:
        """Store generated analyses in the database.

        Args:
            analyses: Generated analyses to store
        """
        # TODO: Implement database storage for analyses
        print(f"TODO: Store {len(analyses)} analyses in database")

    def _generate_evaluations(
        self, analyses: Sequence[Analysis]
    ) -> Sequence[Evaluation]:
        """Generate evaluations using the evaluate prompt template.

        Args:
            analyses: The generated analyses to evaluate

        Returns:
            Generated evaluations
        """
        try:
            # Create GenAI client
            client = genai.Client()

            # Load the evaluate prompt template
            evaluate_template = load_prompt_template("evaluate")

            # Combine analyses into evaluation prompt
            analyses_text = "\n\n".join(
                [
                    f"Analysis {i + 1}: {analysis.build([], 'temp_interaction')}"
                    for i, analysis in enumerate(analyses)
                ]
            )

            # Fill out the prompt template with the analyses
            full_prompt = fill_out_prompt(evaluate_template, content=analyses_text)

            # Generate content using Google GenAI
            response = client.models.generate_content(
                model="gemini-2.0-flash-001", contents=full_prompt
            )

            text = self._extract_text_from_response(response)

            try:
                if hasattr(Evaluation, "parse"):
                    parsed = Evaluation.parse(text)
                    evaluation_id = parsed.get("id", "evaluation_1")
                    evaluation = Evaluation(id=evaluation_id)
                else:
                    evaluation = Evaluation(id="evaluation_1")

                return [evaluation]
            except Exception:
                placeholder_evaluation = Evaluation(id="placeholder_evaluation_1")
                return [placeholder_evaluation]

        except Exception as e:
            # Fallback for development/testing
            placeholder_evaluation = Evaluation(id="placeholder_evaluation_1")
            return [placeholder_evaluation]

    def _extract_text_from_response(self, response: Any) -> str:
        """Tolerantly extract human/model text from various response shapes.

        Handles dicts with keys like 'candidates', 'outputs', 'content', 'text',
        or objects with similar attributes. Falls back to str(response).
        """
        # If it's already a string
        if isinstance(response, str):
            return response

        # If dict-like
        if isinstance(response, dict):
            # common GenAI shapes
            if "candidates" in response and response["candidates"]:
                cand = response["candidates"][0]
                if isinstance(cand, dict):
                    return cand.get("content") or cand.get("text") or str(cand)
                return str(cand)
            if "outputs" in response and response["outputs"]:
                out = response["outputs"][0]
                if isinstance(out, dict):
                    return out.get("content") or out.get("text") or str(out)
                return str(out)
            for key in ("content", "text", "message", "response"):
                if key in response:
                    return response[key]

            # Fallback to JSON string
            try:
                return json.dumps(response)
            except Exception:
                return str(response)

        # If object with attributes
        for attr in ("candidates", "outputs", "content", "text"):
            if hasattr(response, attr):
                val = getattr(response, attr)
                if isinstance(val, list) and val:
                    first = val[0]
                    if isinstance(first, dict):
                        return first.get("content") or first.get("text") or str(first)
                    return str(first)
                if isinstance(val, str):
                    return val

        # Last resort
        return str(response)

    def _store_evaluations_in_database(self, evaluations: Sequence[Evaluation]) -> None:
        """Store generated evaluations in the database.

        Args:
            evaluations: Generated evaluations to store
        """
        # TODO: Implement database storage for evaluations
        print(f"TODO: Store {len(evaluations)} evaluations in database")
