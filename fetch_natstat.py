"""
fetch_natstat.py
Genera natstat_stats.json con datos de Natstat API v4
Ligas: MLB, NPB, CBB
Corre via GitHub Actions una vez al día + antes de partidos
"""

import json, datetime, time, math, requests

TODAY   = datetime.date.today()
SEASON  = TODAY.year
END     = TODAY.strftime("%Y-%m-%d")
KEY     = "74db-1689d0"
BASE    = "https://api.natstat.com/v4"

print(f"[fetch_natstat] {TODAY} season={SEASON}")

def safe(val):
    try:
        if val is None: return None
        f = float(str(val).replace('%','').strip())
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 3)
    except: return str(val).strip() if val else None

def natstat_get(endpoint, level, params={}):
    """Call Natstat API v4"""
    url = f"{BASE}/{endpoint}/{level}/"
    p = {'key': KEY, 'format': 'json', 'max': 1000}
    p.update(params)
    try:
        r = requests.get(url, params=p, timeout=15)
        r.raise_for_status()
        data = r.json()
        if data.get('success') == 0:
            print(f"  API error: {data.get('error',{}).get('message','unknown')}")
            return None
        remaining = data.get('meta',{}).get('X-RateLimit-Remaining','?')
        print(f"  OK {level}/{endpoint} → {data.get('meta',{}).get('Total_Results','?')} results (remaining: {remaining})")
        return data
    except Exception as e:
        print(f"  WARN {level}/{endpoint}: {e}")
        return None

# ════════════════════════════════════════════════════════
# 1. NPB — Partidos de hoy y mañana
# ════════════════════════════════════════════════════════
print("→ NPB games...")
npb_today    = []
npb_tomorrow = []
TOMORROW = (TODAY + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

# Today's games
data = natstat_get('games', 'NPB', {'limit': 'today'})
if data:
    for g in (data.get('games') or {}).values():
        home = g.get('home_team_name','') or g.get('home','')
        away = g.get('away_team_name','') or g.get('away','')
        npb_today.append({
            'game_id':   g.get('id') or g.get('game_id'),
            'home':      home,
            'away':      away,
            'home_id':   g.get('home_team_id') or g.get('home_id'),
            'away_id':   g.get('away_team_id') or g.get('away_id'),
            'date':      TODAY.isoformat(),
            'time':      g.get('time',''),
            'status':    g.get('status',''),
            'hPitcher':  g.get('home_probable_pitcher','TBD') or 'TBD',
            'aPitcher':  g.get('away_probable_pitcher','TBD') or 'TBD',
        })
    print(f"   NPB today: {len(npb_today)} games")

# Tomorrow's games
data = natstat_get('games', 'NPB', {'date': TOMORROW})
if data:
    for g in (data.get('games') or {}).values():
        home = g.get('home_team_name','') or g.get('home','')
        away = g.get('away_team_name','') or g.get('away','')
        npb_tomorrow.append({
            'game_id':   g.get('id') or g.get('game_id'),
            'home':      home,
            'away':      away,
            'home_id':   g.get('home_team_id') or g.get('home_id'),
            'away_id':   g.get('away_team_id') or g.get('away_id'),
            'date':      TOMORROW,
            'time':      g.get('time',''),
            'status':    g.get('status',''),
            'hPitcher':  g.get('home_probable_pitcher','TBD') or 'TBD',
            'aPitcher':  g.get('away_probable_pitcher','TBD') or 'TBD',
        })
    print(f"   NPB tomorrow: {len(npb_tomorrow)} games")

time.sleep(0.5)

# ════════════════════════════════════════════════════════
# 2. NPB — ELO ratings (win probabilities)
# ════════════════════════════════════════════════════════
print("→ NPB ELO...")
npb_elo = {}
data = natstat_get('elo', 'NPB', {'date': TODAY.strftime("%Y-%m-%d")})
if data:
    for entry in (data.get('elo') or {}).values():
        team = entry.get('team_name','') or entry.get('team','')
        npb_elo[team] = {
            'elo':      safe(entry.get('elo') or entry.get('rating')),
            'win_prob': safe(entry.get('win_prob') or entry.get('winprob')),
        }
    print(f"   NPB ELO: {len(npb_elo)} teams")

time.sleep(0.5)

# ════════════════════════════════════════════════════════
# 3. NPB — Pitching stats (season)
# ════════════════════════════════════════════════════════
print("→ NPB pitching stats...")
npb_pitching = []
data = natstat_get('stats', 'NPB', {'type': 'player', 'stat': 'era', 'season': SEASON})
if data:
    for p in (data.get('stats') or {}).values():
        npb_pitching.append({
            'name':  p.get('player_name','') or p.get('name',''),
            'team':  p.get('team_name','') or p.get('team',''),
            'era':   safe(p.get('era') or p.get('ERA')),
            'whip':  safe(p.get('whip') or p.get('WHIP')),
            'ip':    safe(p.get('ip') or p.get('IP')),
            'w':     safe(p.get('w') or p.get('W')),
            'l':     safe(p.get('l') or p.get('L')),
            'k':     safe(p.get('so') or p.get('k') or p.get('K')),
            'bb':    safe(p.get('bb') or p.get('BB')),
            'k9':    safe(p.get('k9') or p.get('K9')),
            'bb9':   safe(p.get('bb9') or p.get('BB9')),
        })
    print(f"   NPB pitching: {len(npb_pitching)}")

time.sleep(0.5)

# ════════════════════════════════════════════════════════
# 4. NPB — Batting stats (season)
# ════════════════════════════════════════════════════════
print("→ NPB batting stats...")
npb_batting = []
data = natstat_get('stats', 'NPB', {'type': 'player', 'stat': 'avg', 'season': SEASON})
if data:
    for p in (data.get('stats') or {}).values():
        npb_batting.append({
            'name':  p.get('player_name','') or p.get('name',''),
            'team':  p.get('team_name','') or p.get('team',''),
            'avg':   safe(p.get('avg') or p.get('AVG')),
            'obp':   safe(p.get('obp') or p.get('OBP')),
            'slg':   safe(p.get('slg') or p.get('SLG')),
            'ops':   safe(p.get('ops') or p.get('OPS')),
            'hr':    safe(p.get('hr') or p.get('HR')),
            'rbi':   safe(p.get('rbi') or p.get('RBI')),
            'ab':    safe(p.get('ab') or p.get('AB')),
        })
    print(f"   NPB batting: {len(npb_batting)}")

time.sleep(0.5)

# ════════════════════════════════════════════════════════
# 5. NPB — Team stats
# ════════════════════════════════════════════════════════
print("→ NPB team stats...")
npb_team_batting  = []
npb_team_pitching = []

data = natstat_get('stats', 'NPB', {'type': 'team', 'stat': 'avg', 'season': SEASON})
if data:
    for t in (data.get('stats') or {}).values():
        npb_team_batting.append({
            'team': t.get('team_name','') or t.get('team',''),
            'avg':  safe(t.get('avg')), 'obp': safe(t.get('obp')),
            'slg':  safe(t.get('slg')), 'ops': safe(t.get('ops')),
        })
    print(f"   NPB team batting: {len(npb_team_batting)}")

data = natstat_get('stats', 'NPB', {'type': 'team', 'stat': 'era', 'season': SEASON})
if data:
    for t in (data.get('stats') or {}).values():
        npb_team_pitching.append({
            'team': t.get('team_name','') or t.get('team',''),
            'era':  safe(t.get('era')), 'whip': safe(t.get('whip')),
            'k9':   safe(t.get('k9')),
        })
    print(f"   NPB team pitching: {len(npb_team_pitching)}")

time.sleep(0.5)

# ════════════════════════════════════════════════════════
# 6. CBB — Partidos de hoy
# ════════════════════════════════════════════════════════
print("→ CBB games today...")
cbb_today = []
data = natstat_get('games', 'CBB', {'limit': 'today'})
if data:
    for g in (data.get('games') or {}).values():
        home = g.get('home_team_name','') or g.get('home','')
        away = g.get('away_team_name','') or g.get('away','')
        cbb_today.append({
            'game_id':  g.get('id') or g.get('game_id'),
            'home':     home,
            'away':     away,
            'home_id':  g.get('home_team_id') or g.get('home_id'),
            'away_id':  g.get('away_team_id') or g.get('away_id'),
            'date':     TODAY.isoformat(),
            'time':     g.get('time',''),
            'status':   g.get('status',''),
            'hPitcher': g.get('home_probable_pitcher','TBD') or 'TBD',
            'aPitcher': g.get('away_probable_pitcher','TBD') or 'TBD',
            'conference': g.get('conference',''),
        })
    print(f"   CBB today: {len(cbb_today)} games")

time.sleep(0.5)

# ════════════════════════════════════════════════════════
# 7. CBB — ELO ratings
# ════════════════════════════════════════════════════════
print("→ CBB ELO...")
cbb_elo = {}
data = natstat_get('elo', 'CBB', {'season': SEASON})
if data:
    for entry in (data.get('elo') or {}).values():
        team = entry.get('team_name','') or entry.get('team','')
        cbb_elo[team] = {
            'elo':      safe(entry.get('elo') or entry.get('rating')),
            'win_prob': safe(entry.get('win_prob') or entry.get('winprob')),
            'rpi':      safe(entry.get('rpi')),
        }
    print(f"   CBB ELO: {len(cbb_elo)} teams")

time.sleep(0.5)

# ════════════════════════════════════════════════════════
# 8. CBB — Pitching stats
# ════════════════════════════════════════════════════════
print("→ CBB pitching stats...")
cbb_pitching = []
data = natstat_get('stats', 'CBB', {'type': 'player', 'stat': 'era', 'season': SEASON})
if data:
    for p in (data.get('stats') or {}).values():
        ip = safe(p.get('ip') or p.get('IP')) or 0
        k  = safe(p.get('so') or p.get('k')) or 0
        bb = safe(p.get('bb') or p.get('BB')) or 0
        hr = safe(p.get('hr') or p.get('HR')) or 0
        era = safe(p.get('era') or p.get('ERA'))
        rec = {
            'name': p.get('player_name','') or p.get('name',''),
            'team': p.get('team_name','') or p.get('team',''),
            'era':  era, 'whip': safe(p.get('whip') or p.get('WHIP')),
            'ip':   ip,  'w':    safe(p.get('w') or p.get('W')),
            'l':    safe(p.get('l') or p.get('L')),
            'k':    k,   'bb':   bb,
        }
        # Compute K/9, BB/9, FIP
        if ip and ip > 0:
            rec['k9']  = round(k / ip * 9, 2)
            rec['bb9'] = round(bb / ip * 9, 2)
            rec['fip'] = round((13*hr + 3*bb - 2*k) / ip + 3.20, 2)
        cbb_pitching.append(rec)
    print(f"   CBB pitching: {len(cbb_pitching)}")

time.sleep(0.5)

# ════════════════════════════════════════════════════════
# 9. CBB — Batting stats
# ════════════════════════════════════════════════════════
print("→ CBB batting stats...")
cbb_batting = []
data = natstat_get('stats', 'CBB', {'type': 'player', 'stat': 'avg', 'season': SEASON})
if data:
    for p in (data.get('stats') or {}).values():
        obp = safe(p.get('obp') or p.get('OBP'))
        slg = safe(p.get('slg') or p.get('SLG'))
        rec = {
            'name': p.get('player_name','') or p.get('name',''),
            'team': p.get('team_name','') or p.get('team',''),
            'avg':  safe(p.get('avg') or p.get('AVG')),
            'obp':  obp, 'slg':  slg,
            'hr':   safe(p.get('hr') or p.get('HR')),
            'rbi':  safe(p.get('rbi') or p.get('RBI')),
            'ab':   safe(p.get('ab') or p.get('AB')),
            'bb':   safe(p.get('bb') or p.get('BB')),
        }
        if obp and slg:
            try: rec['ops'] = round(float(obp)+float(slg), 3)
            except: pass
        cbb_batting.append(rec)
    print(f"   CBB batting: {len(cbb_batting)}")

time.sleep(0.5)

# ════════════════════════════════════════════════════════
# 10. CBB — Team stats + RPI
# ════════════════════════════════════════════════════════
print("→ CBB team stats...")
cbb_team_stats = []
data_bat = natstat_get('stats', 'CBB', {'type': 'team', 'stat': 'avg', 'season': SEASON})
data_pit = natstat_get('stats', 'CBB', {'type': 'team', 'stat': 'era', 'season': SEASON})

team_pit_map = {}
if data_pit:
    for t in (data_pit.get('stats') or {}).values():
        name = t.get('team_name','') or t.get('team','')
        team_pit_map[name] = {'era': safe(t.get('era')), 'whip': safe(t.get('whip'))}

if data_bat:
    for t in (data_bat.get('stats') or {}).values():
        name = t.get('team_name','') or t.get('team','')
        obp = safe(t.get('obp')); slg = safe(t.get('slg'))
        rec = {
            'team': name,
            'avg':  safe(t.get('avg')), 'obp': obp, 'slg': slg,
            'era':  team_pit_map.get(name,{}).get('era'),
            'whip': team_pit_map.get(name,{}).get('whip'),
            'rpi':  cbb_elo.get(name,{}).get('rpi'),
            'elo':  cbb_elo.get(name,{}).get('elo'),
        }
        if obp and slg:
            try: rec['ops'] = round(float(obp)+float(slg), 3)
            except: pass
        cbb_team_stats.append(rec)
    print(f"   CBB team stats: {len(cbb_team_stats)}")

time.sleep(0.5)

# ════════════════════════════════════════════════════════
# 11. MLB — ELO (complemento al modelo existente)
# ════════════════════════════════════════════════════════
print("→ MLB ELO...")
mlb_elo = {}
data = natstat_get('elo', 'MLB', {'date': TODAY.strftime("%Y-%m-%d")})
if data:
    for entry in (data.get('elo') or {}).values():
        team = entry.get('team_name','') or entry.get('team','')
        mlb_elo[team] = {
            'elo':      safe(entry.get('elo') or entry.get('rating')),
            'win_prob': safe(entry.get('win_prob') or entry.get('winprob')),
        }
    print(f"   MLB ELO: {len(mlb_elo)} teams")

# ════════════════════════════════════════════════════════
# 12. Output
# ════════════════════════════════════════════════════════
output = {
    "generated_at":       TODAY.isoformat(),
    "season":             SEASON,
    # NPB
    "npb_games_today":    npb_today,
    "npb_games_tomorrow": npb_tomorrow,
    "npb_elo":            npb_elo,
    "npb_pitching":       npb_pitching,
    "npb_batting":        npb_batting,
    "npb_team_batting":   npb_team_batting,
    "npb_team_pitching":  npb_team_pitching,
    # CBB (NCAA Baseball)
    "cbb_games_today":    cbb_today,
    "cbb_elo":            cbb_elo,
    "cbb_pitching":       cbb_pitching,
    "cbb_batting":        cbb_batting,
    "cbb_team_stats":     cbb_team_stats,
    # MLB supplement
    "mlb_elo":            mlb_elo,
}

with open("natstat_stats.json", "w", encoding="utf-8") as f:
    json.dump(output, f, separators=(",",":"))

size_kb = len(json.dumps(output)) / 1024
print(f"\n✅ natstat_stats.json — {size_kb:.1f} KB")
print(f"   NPB: {len(npb_today)} hoy | {len(npb_tomorrow)} mañana | {len(npb_pitching)} pitchers | {len(npb_batting)} bateadores")
print(f"   CBB: {len(cbb_today)} hoy | {len(cbb_pitching)} pitchers | {len(cbb_batting)} bateadores | {len(cbb_team_stats)} equipos")
print(f"   MLB ELO: {len(mlb_elo)} equipos")
