"""Configure sys.path so test modules can import from backend/ and repo root."""
import sys
import os

# Add backend/ to path for `app.*` imports
BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

# Add repo root to path for `ai.*` imports
ROOT = os.path.abspath(os.path.join(BACKEND, ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
