import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

for path in [PROJECT_ROOT, os.path.join(PROJECT_ROOT, 'backend')]:
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.main import app
