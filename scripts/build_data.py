import json
from pathlib import Path

DATA_DIR = Path("data")

def load_json(filename):
    path = DATA_DIR / filename
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

data = {
    "leagues": load_json("leagues.json"),
    "seasons": load_json("seasons.json"),
    "teams": load_json("teams.json"),
    "matches": load_json("matches.json"),
    "standings": load_json("standings.json"),
    "players": load_json("players.json"),
    "news": load_json("news.json")
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ data.json generated successfully")
