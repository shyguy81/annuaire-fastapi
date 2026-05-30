"""
Pytest configuration for RAP integration tests.

This conftest.py ensures that tests can import modules from the parent directory.
"""

import sys
from pathlib import Path

# Add the app root directory to Python path so tests can import app modules
app_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(app_root))
