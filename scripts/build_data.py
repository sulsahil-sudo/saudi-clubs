# Build data.json from modular files

import json
from pathlib import Path

DATA_DIR = Path("data")

files = {
    "leagues": DATA_DIR / "leagues.json",
    "seasons": DATA_DIR / "seasons.json",
    "matches": DATA_DIR / "matches.json",
    "standings": DATA_DIR / "standings.json",
    "players": DATA_DIR / "players.json",
}

print("Build system ready")

for name, file in files.items():
    print(f"Checking: {name} -> {file}")
