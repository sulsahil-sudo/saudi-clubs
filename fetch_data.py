import json, urllib.request
from datetime import datetime

ESPN_STANDINGS = "https://site.api.espn.com/apis/v2/sports/soccer/ksa.1/standings"
ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/soccer/ksa.1/scoreboard"
ESPN_LEADERS = "https://site.web.api.espn.com/apis/common/v3/sports/soccer/ksa.1/leaders"
ESPN_ATHLETES = "https://site.api.espn.com/apis/site/v2/sports/soccer/ksa.1/athletes?limit=100&active=true"

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
    print(f"الترتيب: {len(standings)} فريق")
except Exception as ex:
    print("خطأ في الترتيب:", ex)

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
    print("خطأ في المباريات:", ex)

# 3. الهدافون - نجرب عدة endpoints
scorers = []
try:
    leaders = fetch_json(ESPN_LEADERS)
    # محاولة استخراج الهدافين من leaders
    if "leaders" in leaders:
        for cat in leaders["leaders"]:
            if cat.get("name") in ("goals", "totalGoals") or "goal" in cat.get("name","").lower():
                for item in cat.get("leaders", [])[:20]:
                    athlete = item.get("athlete", {})
                    team = athlete.get("team", {}) or item.get("team", {})
                    scorers.append({
                        "name": athlete.get("displayName", "غير معروف"),
                        "team": tr(team.get("displayName", "")),
                        "goals": str(item.get("value", 0)).split(".")[0],
                        "assists": "0"
                    })
                break
except Exception as ex:
    print("محاولة leaders فشلت:", ex)

# إذا لم نجد هدافين، نجرب athletes
if not scorers:
    try:
        ath = fetch_json(ESPN_ATHLETES)
        for item in ath.get("athletes", [])[:30]:
            # نحتاج إحصائيات لكل لاعب - هذا بطيء، لذلك نكتفي بالبيانات الأساسية
            pass
    except Exception as ex:
        print("محاولة athletes فشلت:", ex)

print(f"الهدافون: {len(scorers)}")

# حفظ
output = {
    "standings": standings,
    "results": results,
    "scorers": scorers,
    "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("تم الحفظ بنجاح")
