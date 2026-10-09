import json, urllib.request, sys
from datetime import datetime

ESPN = "https://site.api.espn.com/apis/v2/sports/soccer/ksa.1/standings"
ESPN_SB = "https://site.api.espn.com/apis/site/v2/sports/soccer/ksa.1/scoreboard"

translations = {
    "Al Hilal":"الهلال","Al Ittihad":"الاتحاد","Al Nassr":"النصر","Al Qadsiah":"القادسية",
    "Neom SC":"نيوم","Al Ahli":"الأهلي","Al Kholood":"الخلود","Al Diriyah":"الدرعية",
    "Al Ettifaq":"الاتفاق","Al Hazem":"الحزم","Al Riyadh":"الرياض","Al Fayha":"الفيحاء",
    "Al Khaleej":"الخليج","Al Shabab":"الشباب","Al Fateh":"الفتح","Al Faisaly":"الفيصلي",
    "Al Taawoun":"التعاون","Abha":"أبها"
}

def tr(name): return translations.get(name, name)

# جلب الترتيب
req = urllib.request.Request(ESPN, headers={"User-Agent":"Mozilla/5.0"})
data = json.loads(urllib.request.urlopen(req, timeout=30).read())
entries = data["children"][0]["standings"]["entries"]

standings = []
for e in entries:
    s = {x["name"]: x["displayValue"] for x in e["stats"]}
    standings.append({
        "r": int(s.get("rank",0)),
        "t": tr(e["team"]["displayName"]),
        "p": s.get("gamesPlayed","0"),
        "w": s.get("wins","0"),
        "d": s.get("ties","0"),
        "l": s.get("losses","0"),
        "gf": s.get("pointsFor","0"),
        "ga": s.get("pointsAgainst","0"),
        "gd": s.get("pointDifferential","0"),
        "pts": s.get("points","0")
    })

# جلب النتائج
results = []
try:
    req2 = urllib.request.Request(ESPN_SB, headers={"User-Agent":"Mozilla/5.0"})
    sb = json.loads(urllib.request.urlopen(req2, timeout=30).read())
    for ev in sb.get("events", []):
        c = ev["competitions"][0]
        home = next((x for x in c["competitors"] if x["homeAway"]=="home"), None)
        away = next((x for x in c["competitors"] if x["homeAway"]=="away"), None)
        if home and away:
            results.append({
                "home": tr(home["team"]["displayName"]),
                "away": tr(away["team"]["displayName"]),
                "hs": home.get("score","0"),
                "as": away.get("score","0"),
                "date": ev["date"],
                "status": ev["status"]["type"]["detail"]
            })
except Exception as ex:
    print("تعذر جلب النتائج:", ex)

output = {
    "standings": standings,
    "results": results,
    "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"تم حفظ {len(standings)} فريق و {len(results)} مباراة")
