import json
from pathlib import Path

DATA_DIR = Path("data")

def load_file(name):
    path = DATA_DIR / name
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

output = {
    "leagues": load_file("leagues.json"),
    "seasons": load_file("seasons.json"),
    "teams": load_file("teams.json"),
    "matches": load_file("matches.json"),
    "standings": load_file("standings.json"),
    "players": load_file("players.json"),
    "news": load_file("news.json")
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("data.json created")
