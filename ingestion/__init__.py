"""
Cinema Explorer Ingestion Package.

Data ingestion, normalization, and classification pipeline for TMDB metadata.
"""

import sys
from pathlib import Path

# Ensure backend directory is in sys.path so 'app.models' and 'app.db' are accessible
_BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))
