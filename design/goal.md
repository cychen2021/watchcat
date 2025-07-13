# Goals of Watchcat

The core goal of Watchcat is to collect and analyze information from various sources to extract insights of the user's interests. At the same time, it keeps improving an approximation of the user's interests based on the collected data and feedback from the user.

## Specific Objectives

- Integrate diverse data sources including arXiv, email, RSS feeds, and databases.
- Support both real-time and scheduled batch data collection modes.
- Analyze and summarize collected information using natural language processing and machine learning techniques.
- Continuously learn user preferences through interaction tracking and feedback loops to refine future insights.
- Provide configurable alerting and notification mechanisms based on user-defined criteria and thresholds.
- Offer an extensible plugin architecture to easily add new data sources and analysis modules.
- Present insights through interactive dashboards, visual reports, and exportable summaries.

## Architectural Overview

Watchcat is built on a modular architecture with the following components:

- **Data Pullers:** Connect to various sources (e.g., arXiv API, email servers, RSS feeds) to retrieve raw data.
- **Datastore:** Centralized storage using SQLite or other databases, supporting versioning and checkpointing of datasets.
- **Processing Pipeline:** Chain of tasks including cleansing, transformation, analysis, and summarization.
- **User Model:** Maintains and updates an approximation of the user's interests, feeding back into the pipeline. A potential design for this component is detailed below.

  - **Database Schema:** The model can be implemented with a dedicated table, for instance `user_interests`:
    - `id` (Primary Key)
    - `user_id`
    - `description` (Text): A natural language description of the interest (e.g., "The user is interested in AI").
    - `weight` (Float): The strength of the interest, optional, defaults to 1.0.
    - `embedding` (Vector): The semantic vector calculated from the `description`.
    - `updated_at` (Timestamp)

  - **Model and Update Process:**
    - **a. Initialization:** On first use, an LLM is prompted (e.g., "Summarize the user's interest in one sentence") to generate an initial `description`. An open-source model (like `sentence-transformers`) is then used to compute and store the `embedding`.
    - **b. User Feedback:** Collect user feedback (e.g., "I want to know more about the applications of GPT-4"). Construct a new prompt: "Based on the current description '...' and new feedback '...', update the user interest description in a single sentence and provide an updated interest strength (0-1)." The LLM returns a new `description` and `weight`. A new `embedding` is recalculated, and the database record is updated.

  - **Querying and Application:** When recommending or filtering content:
    1. Retrieve all `user_interests` embeddings.
    2. Compute the embedding for the candidate content.
    3. Calculate the cosine similarity between the content embedding and the user's interest embeddings.
    4. Rank the results based on the score (`similarity * weight`) to find the best match.

  - **Potential Enhancements:**
    - Support multiple, categorized interest records per user.
    - Periodically invoke an LLM to monitor for "interest drift" over time.
    - Use feedback and historical interaction logs as additional context for the LLM to improve the accuracy of updates.

- **Notification Engine:** Monitors processed results against user-defined rules to trigger alerts and deliver summaries.
- **Plugin Interface:** Defines standards for developing and integrating new data pullers, processors, and notification strategies.
- **CLI & API:** Provides command-line and programmatic interfaces for custom workflows and integration into larger systems.