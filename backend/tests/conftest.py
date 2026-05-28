"""Configure sys.path and test env vars so test modules can import cleanly."""
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

# Provide dummy env vars so SQLAlchemy engine creation and config don't crash
# during collection when no .env is present (CI / local without credentials).
_DUMMY_VARS = {
    "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
    "REDIS_URL": "redis://localhost:6379",
    "CLERK_SECRET_KEY": "sk_test_dummy",
    "CLERK_PUBLISHABLE_KEY": "pk_test_dummy",
    "CLERK_WEBHOOK_SECRET": "whsec_dummy",
    "GROQ_API_KEY": "gsk_dummy",
    "OPENROUTER_API_KEY": "sk-or-dummy",
    "R2_BUCKET": "test-bucket",
    "R2_ENDPOINT": "https://test.r2.cloudflarestorage.com",
    "R2_ACCESS_KEY": "dummy",
    "R2_SECRET_KEY": "dummy",
    "GOOGLE_MAPS_API_KEY": "AIza_dummy",
}
for k, v in _DUMMY_VARS.items():
    os.environ.setdefault(k, v)
