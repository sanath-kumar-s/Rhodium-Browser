import os
from pathlib import Path
from PyQt6.QtGui import QIcon

# ── Icon helper ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
ICONS_DIR = BASE_DIR / "style" / "icons"

def icon(name: str) -> QIcon:
    return QIcon(str(ICONS_DIR / name))
