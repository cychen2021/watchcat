# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "ruff",
#     "sh",
# ]
# ///
import os
import sh

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))


def main() -> None:
    files = list(
        map(
            lambda f: os.path.join(PROJECT_ROOT, f),
            ["src", *[f for f in os.listdir(PROJECT_ROOT) if f.endswith(".py")]],
        )
    )
    sh.uvx("ruff", "format", *files)


if __name__ == "__main__":
    main()
