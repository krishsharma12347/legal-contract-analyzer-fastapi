from pathlib import Path
import sys

# Ensure the inner `fastapi` app directory is importable
PROJECT_ROOT = Path(__file__).parent
INNER_APP_DIR = PROJECT_ROOT / "fastapi"

if str(INNER_APP_DIR) not in sys.path:
    sys.path.insert(0, str(INNER_APP_DIR))

# Import the FastAPI app defined in fastapi/main.py
from main import app  # type: ignore  # FastAPI app object

