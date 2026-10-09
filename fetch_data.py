import json, urllib.request
from datetime import datetime

ESPN_STANDINGS = "https://site.api.espn.com/apis/v2/sports/soccer/ksa.1/standings"
ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/soccer/ksa.1/scoreboard"
ESPN_ATHLETES = "https://site.api.espn.com/apis/site/v2/sports/soccer/ksa.1/athletes?limit=200&active=true"

translations = {
    "Al Hilal":"الهلال","Al Ittihad":"الاتحاد","Al Nassr":"النصر","Al Qadsiah":"القادسية",
    "Neom SC":"نيوم","Al Ahli":"الأهلي","Al Kholood":"الخلود","Al Diriyah":"الدرعية",
    "Al Ettifaq":"الاتفاق","Al Hazem":"الحزم","Al Riyadh":"الرياض","Al Fayha":"الفيحاء",
    "Al Khaleej":"الخليج","Al Shabab":"الشباب","Al Fateh":"الفتح","Al Faisaly":"الفيصلي",
    "Al Taawoun":"التعاون","Abha":"أبها"
}
def tr(name): return translations.get(name, name)

def fetch_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

# 1. الترتيب
standings = []
try:
    data = fetch_json(ESPN_STANDINGS)
    entries = data["children"][0]["standings"]["entries"]
    for e in entries:
        s = {x["name"]: x["displayValue"] for x in e["stats"]}
        standings.append({
            "r": int(s.get("rank", 0)),
            "t": tr(e["team"]["displayName"]),
            "p": s.get("gamesPlayed", "0"),
            "w": s.get("wins", "0"),
            "d": s.get("ties", "0"),
            "l": s.get("losses", "0"),
            "gf": s.get("pointsFor", "0"),
            "ga": s.get("pointsAgainst", "0"),
            "gd": s.get("pointDifferential", "0"),
            "pts": s.get("points", "0")
        })
    print(f"الترتيب: {len(standings)}")
except Exception as ex:
    print("خطأ الترتيب:", ex)

# 2. المباريات
results = []
try:
    sb = fetch_json(ESPN_SCOREBOARD)
    for ev in sb.get("events", []):
        c = ev["competitions"][0]
        home = next((x for x in c["competitors"] if x["homeAway"] == "home"), None)
        away = next((x for x in c["competitors"] if x["homeAway"] == "away"), None)
        if home and away:
            results.append({
                "home": tr(home["team"]["displayName"]),
                "away": tr(away["team"]["displayName"]),
                "hs": home.get("score", "0"),
                "as": away.get("score", "0"),
                "date": ev["date"],
                "status": ev["status"]["type"]["detail"]
            })
    print(f"المباريات: {len(results)}")
except Exception as ex:
    print("خطأ المباريات:", ex)

# 3. اللاعبون
players = []
try:
    ath = fetch_json(ESPN_ATHLETES)
    for item in ath.get("athletes", []):
        team = item.get("team", {}) or {}
        position = item.get("position", {}) or {}
        players.append({
            "name": item.get("displayName", ""),
            "team": tr(team.get("displayName", "")),
            "position": position.get("abbreviation", position.get("name", "")),
            "number": str(item.get("jersey", "")),
            "age": str(item.get("age", "")),
            "nationality": item.get("citizenship", "")
        })
    print(f"اللاعبون: {len(players)}")
except Exception as ex:
    print("خطأ اللاعبين:", ex)

output = {
    "standings": standings,
    "results": results,
    "scorers": [],
    "players": players,
    "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("تم الحفظ")
