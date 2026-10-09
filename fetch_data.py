import json, urllib.request
from datetime import datetime, timedelta

ESPN_STANDINGS = "https://site.api.espn.com/apis/v2/sports/soccer/ksa.1/standings"
ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/ksa.1/scoreboard"

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
team_ids = []
try:
    data = fetch_json(ESPN_STANDINGS)
    entries = data["children"][0]["standings"]["entries"]
    for e in entries:
        s = {x["name"]: x["displayValue"] for x in e["stats"]}
        team_name = tr(e["team"]["displayName"])
        team_ids.append((e["team"]["id"], team_name))
        standings.append({
            "r": int(s.get("rank", 0)),
            "t": team_name,
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

# 2. المباريات - نجرب عدة مصادر
def parse_event(ev):
    c = ev["competitions"][0]
    home = next((x for x in c["competitors"] if x["homeAway"] == "home"), None)
    away = next((x for x in c["competitors"] if x["homeAway"] == "away"), None)
    if not home or not away:
        return None
    status_type = ev.get("status", {}).get("type", {})
    return {
        "home": tr(home["team"]["displayName"]),
        "away": tr(away["team"]["displayName"]),
        "hs": home.get("score", "0"),
        "as": away.get("score", "0"),
        "date": ev["date"],
        "status": status_type.get("detail", ""),
        "state": status_type.get("state", ""),
        "completed": status_type.get("completed", False),
        "clock": ev.get("status", {}).get("displayClock", ""),
        "period": ev.get("status", {}).get("period", 0)
    }

results = []
seen = set()

def add_events(events):
    for ev in events:
        m = parse_event(ev)
        if m:
            key = m["home"] + "|" + m["away"] + "|" + m["date"]
            if key not in seen:
                seen.add(key)
                results.append(m)

# محاولة 1: الرابط الأساسي (مباريات اليوم)
try:
    sb = fetch_json(ESPN_BASE, timeout=30)
    events = sb.get("events", [])
    print(f"الرابط الأساسي: {len(events)} مباراة")
    add_events(events)
except Exception as ex:
    print("خطأ الأساسي:", ex)

# محاولة 2: أيام محددة (-7 إلى +7)
today = datetime.utcnow()
for i in range(-7, 8):
    d = (today + timedelta(days=i)).strftime("%Y%m%d")
    try:
        url = f"{ESPN_BASE}?dates={d}"
        sb = fetch_json(url, timeout=20)
        events = sb.get("events", [])
        if events:
            print(f"{d}: {len(events)} مباراة")
            add_events(events)
    except Exception as ex:
        pass

print(f"المباريات (بدون تكرار): {len(results)}")

# 3. اللاعبون
players = []
for team_id, team_name in team_ids:
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/ksa.1/teams/{team_id}/roster"
        roster = fetch_json(url, timeout=20)
        for ath in roster.get("athletes", []):
            pos = ath.get("position", {}) or {}
            players.append({
                "name": ath.get("displayName", ""),
                "team": team_name,
                "position": pos.get("abbreviation", ""),
                "number": str(ath.get("jersey", "")),
                "age": str(ath.get("age", "")),
                "nationality": ath.get("citizenship", "") or ath.get("birthPlace", {}).get("country", "")
            })
    except Exception as ex:
        print(f"خطأ {team_name}:", ex)

print(f"مجموع اللاعبين: {len(players)}")

output = {
    "standings": standings,
    "results": results,
    "players": players,
    "scorers": [],
    "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("تم الحفظ")
