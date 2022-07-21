"""
Unit and regression test for the openffpydantic package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import openffpydantic


def test_openffpydantic_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "openffpydantic" in sys.modules
