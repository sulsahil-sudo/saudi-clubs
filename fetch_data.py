import json, urllib.request, urllib.parse, os
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

def fetch_direct(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9"
    })
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

def fetch_via_proxy(url, timeout=40):
    proxies = [
        "https://api.allorigins.win/raw?url=" + urllib.parse.quote(url, safe=''),
        "https://api.codetabs.com/v1/proxy?quest=" + urllib.parse.quote(url, safe=''),
        "https://corsproxy.io/?url=" + urllib.parse.quote(url, safe='')
    ]
    for p in proxies:
        try:
            print(f"  محاولة بروكسي: {p[:50]}...")
            result = fetch_direct(p, timeout=timeout)
            print(f"  ✅ نجح")
            return result
        except Exception as ex:
            print(f"  ❌ فشل: {str(ex)[:80]}")
    return None

def fetch_smart(url, timeout=30):
    try:
        return fetch_direct(url, timeout=timeout)
    except Exception as ex:
        print(f"  مباشر فشل: {str(ex)[:80]}")
        return fetch_via_proxy(url, timeout=timeout)

# 1. الترتيب
standings = []
team_ids = []
try:
    print("جلب الترتيب...")
    data = fetch_smart(ESPN_STANDINGS)
    if data:
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

# 2. المباريات
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

# الرابط الأساسي
print("\nجلب المباريات (الرابط الأساسي)...")
try:
    sb = fetch_smart(ESPN_BASE, timeout=30)
    if sb:
        events = sb.get("events", [])
        print(f"عدد الأحداث: {len(events)}")
        add_events(events)
except Exception as ex:
    print("خطأ:", ex)

# أيام منفصلة - من -21 إلى +21
print("\nجلب المباريات (أيام منفصلة من -21 إلى +21)...")
today = datetime.utcnow()
for i in range(-21, 22):
    d = (today + timedelta(days=i)).strftime("%Y%m%d")
    try:
        url = f"{ESPN_BASE}?dates={d}"
        sb = fetch_smart(url, timeout=20)
        if sb:
            events = sb.get("events", [])
            if events:
                print(f"  {d}: {len(events)} مباراة")
                add_events(events)
    except Exception as ex:
        pass

print(f"\nمجموع المباريات: {len(results)}")

# 3. اللاعبون
players = []
print("\nجلب اللاعبين...")

for team_id, team_name in team_ids:
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/ksa.1/teams/{team_id}/roster"
        roster = fetch_smart(url, timeout=20)

        if roster:
            for ath in roster.get("athletes", []):
                pos = ath.get("position", {}) or {}
                
                players.append({
                    "player_id": f"{team_id}-{ath.get('displayName','').lower().replace(' ','-')}",
                    "team_id": str(team_id),
                    "team": team_name,
                    "name": ath.get("displayName", ""),
                    "position": pos.get("abbreviation", ""),
                    "number": str(ath.get("jersey", "")),
                    "age": str(ath.get("age", "")),
                    "nationality": ath.get("citizenship", "") or ath.get("birthPlace", {}).get("country", "")
                })
    except Exception as ex:
        print(f"  خطأ {team_name}: {str(ex)[:50]}")

print(f"مجموع اللاعبين: {len(players)}")

# إنشاء مجلد data إذا لم يكن موجوداً
os.makedirs("data", exist_ok=True)

# حفظ الملفات الفرعية
with open("data/standings.json", "w", encoding="utf-8") as f:
    json.dump(standings, f, ensure_ascii=False, indent=2)

with open("data/matches.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with open("data/players.json", "w", encoding="utf-8") as f:
    json.dump(players, f, ensure_ascii=False, indent=2)

teams = []
for team_id, team_name in team_ids:
    teams.append({
        "team_id": str(team_id),
        "league_id": "saudi-pro-league",
        "name_ar": team_name
    })

with open("data/teams.json", "w", encoding="utf-8") as f:
    json.dump(teams, f, ensure_ascii=False, indent=2)

# 4. الهدافون
scorers = []
assists = []
try:
    print("\nجلب الهدافين...")
    data = fetch_smart(
        "https://site.api.espn.com/apis/site/v2/sports/soccer/ksa.1/statistics"
    )
    if data:
        for stat in data.get("stats", []):
            if stat.get("name") == "goalsLeaders":
                for p in stat.get("leaders", []):
                    scorers.append({
                        "name": p["athlete"]["displayName"],
                        "team": tr(p["athlete"]["team"]["displayName"]),
                        "goals": int(p["value"])
                    })
    
               for p in stat.get("leaders", []):

    assist_count = 0

    for st in p.get("statistics", []):
        if st.get("name") == "goalAssists":
            assist_count = int(st.get("value", 0))

    assists.append({
        "name": p["athlete"]["displayName"],
        "team": tr(p["athlete"]["team"]["displayName"]),
        "assists": assist_count
    })
    print(f"عدد الهدافين: {len(scorers)}")
except Exception as ex:
    print("خطأ الهدافين:", ex)

output = {
    "standings": standings,
    "results": results,
    "players": players,
    "scorers": scorers,
"assists": assists,


    "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n✅ تم الحفظ بنجاح")
