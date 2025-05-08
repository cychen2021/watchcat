import os
import subprocess

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))


def main() -> None:
    subprocess.run(["black", PROJECT_ROOT])


if __name__ == "__main__":
    main()
