from enum import Enum


class State:
    INIT = "init"
    PULLING = "pulling"
    SUMMARIZING = "summarizing"
    EVALUATING = "evaluating"
    FEEDBACK = "feedback"
    DONE = "done"


class Automaton: ...
