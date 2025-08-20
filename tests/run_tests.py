"""Test runner for all puller tests."""

import pytest
import sys
from pathlib import Path

def run_tests():
    """Run all tests in the puller module."""
    test_dir = Path(__file__).parent / "puller"
    return pytest.main([str(test_dir), "-v"])

if __name__ == "__main__":
    sys.exit(run_tests())
