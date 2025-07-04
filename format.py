# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "ruff",
# ]
# ///
import os
import subprocess
import sys

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))


def main() -> None:
    files = list(
        map(
            lambda f: os.path.join(PROJECT_ROOT, f),
            ["src", *[f for f in os.listdir(PROJECT_ROOT) if f.endswith(".py")]],
        )
    )
    subprocess.run(
        ["uvx", "ruff", "format", *files],
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


if __name__ == "__main__":
    main()
