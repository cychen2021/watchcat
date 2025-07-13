"""State management for the Watchcat workflow automaton."""

from enum import Enum


class State(Enum):
    """States of the Watchcat workflow automaton."""

    INIT = "init"
    PULLING = "pulling"
    SUMMARIZING = "summarizing"
    EVALUATING = "evaluating"
    FEEDBACK = "feedback"
    DONE = "done"
