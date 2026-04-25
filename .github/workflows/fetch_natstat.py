"""
fetch_natstat.py v2
Genera natstat_stats.json con datos de Natstat API v4
Base URL: https://api4.natst.at/{key}/{endpoint}/{level}/
Ligas: MLB, NPB, CBB
"""

import json, datetime, time, math, requests

TODAY    = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
SEASON   = TODAY.year
KEY      = "74db-1689d0"
BASE     = f"https://api4.natst.at/{KEY}"

print(f"[fetch_natstat v2] {TODAY} season={SEASON}")
print(f"   BASE: {BASE}")

def safe(val):
    try:
        if val is None: return None
        f = float(str(val).replace('%','').strip())
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 3)
    except: return str(val).strip() if val else None

def natstat_get(endpoint, level, params={}):
    """Call Natstat API v4 — format: /key/endpoint/level/"""
    url = f"{BASE}/{endpoint}/{level}/"
    p = {'format': 'json', 'max': 1000}
    p.update(params)
    try:
        r = requests.get(url, params=p, timeout=15)
        print(f"  {r.status_code} {level}/{endpoint} → {url[:60]}")
        if r.status_code == 404:
            print(f"  404 — endpoint not found")
            return None
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and data.get('success') == 0:
            print(f"  API error: {data.get('error',{})}")
            return None
        total = data.get('meta',{}).get('Total_Results','?') if isinstance(data, dict) else '?'
        remaining = data.get('meta',{}).get('X-RateLimit-Remaining','?') if isinstance(data, dict) else '?'
        print(f"  OK → {total} results (remaining: {remaining})")
        return data
    except Exception as e:
        print(f"  WARN {level}/{endpoint}: {e}")
        return None

def parse_games(data, date_str):
    """Parse games from Natstat response"""
    games = []
    if not data: return games
    # Try different response structures
    game_list = (data.get('games') or data.get('data') or data.get('results') or {})
    if isinstance(game_list, dict):
        game_list = list(game_list.values())
    elif not isinstance(game_list, list):
        game_list = []
    for g in game_list:
        if not isinstance(g, dict): continue
        # Try different field names for home/away
        home = (g.get('home_team_name') or g.get('home_name') or
                g.get('home') or g.get('hteam') or '')
        away = (g.get('away_team_name') or g.get('away_name') or
                g.get('away') or g.get('ateam') or '')
        if not home and not away: continue
        games.append({
            'game_id':  str(g.get('id') or g.get('game_id') or ''),
            'home':     home,
            'away':     away,
            'home_id':  g.get('home_team_id') or g.get('home_id') or '',
            'away_id':  g.get('away_team_id') or g.get('away_id') or '',
            'date':     date_str,
            'time':     g.get('time') or g.get('game_time') or '',
            'status':   g.get('status') or '',
            'hPitcher': g.get('home_probable_pitcher') or g.get('hpitcher') or 'TBD',
            'aPitcher': g.get('away_probable_pitcher') or g.get('apitcher') or 'TBD',
        })
    return games

def parse_stats(data, stat_type='pitcher'):
    """Parse player/team stats from Natstat response"""
    records = []
    if not data: return records
    items = (data.get('stats') or data.get('data') or data.get('results') or data.get('players') or {})
    if isinstance(items, dict): items = list(items.values())
    elif not isinstance(items, list): items = []
    for p in items:
        if not isinstance(p, dict): continue
        name = (p.get('player_name') or p.get('name') or p.get('player') or
                p.get('team_name') or p.get('team') or '')
        team = (p.get('team_name') or p.get('team') or '')
        rec = {'name': name, 'team': team}
        # Map all numeric fields
        for field in ['era','ERA','whip','WHIP','ip','IP','w','W','l','L',
                      'k','K','so','SO','bb','BB','hr','HR','k9','K9','bb9','BB9',
                      'avg','AVG','obp','OBP','slg','SLG','ops','OPS','rbi','RBI',
                      'ab','AB','fip','FIP','era_adj','whip_adj']:
            val = p.get(field)
            if val is not None:
                key = field.lower()
                rec[key] = safe(val)
        if name: records.append(rec)
    return records

def parse_elo(data):
    """Parse ELO ratings"""
    result = {}
    if not data: return result
    items = (data.get('elo') or data.get('data') or data.get('results') or {})
    if isinstance(items, dict): items = list(items.values())
    elif not isinstance(items, list): items = []
    for e in items:
        if not isinstance(e, dict): continue
        team = (e.get('team_name') or e.get('team') or e.get('name') or '')
        if team:
            result[team] = {
                'elo':      safe(e.get('elo') or e.get('rating') or e.get('elo_rating')),
                'win_prob': safe(e.get('win_prob') or e.get('winprob') or e.get('prob')),
                'rpi':      safe(e.get('rpi')),
            }
    return result

# ════════════════════════════════════════════════════════
# First: check datastatus to confirm API works
# ════════════════════════════════════════════════════════
print("→ Testing API connection (datastatus)...")
for level in ['NPB', 'CBB', 'MLB']:
    data = natstat_get('datastatus', level)
    if data:
        print(f"  ✅ {level} connected")
    time.sleep(0.3)

# ════════════════════════════════════════════════════════
# NPB
# ════════════════════════════════════════════════════════
print("\n→ NPB games today...")
npb_today = parse_games(
    natstat_get('games', 'npb', {'limit': 'today'}),
    TODAY.isoformat()
)
print(f"   {len(npb_today)} games")
time.sleep(0.5)

print("→ NPB games tomorrow...")
npb_tomorrow = parse_games(
    natstat_get('games', 'npb', {'date': TOMORROW.strftime('%Y-%m-%d')}),
    TOMORROW.isoformat()
)
print(f"   {len(npb_tomorrow)} games")
time.sleep(0.5)

print("→ NPB ELO...")
npb_elo = parse_elo(natstat_get('elo', 'npb', {'season': SEASON}))
print(f"   {len(npb_elo)} teams")
time.sleep(0.5)

print("→ NPB pitching...")
npb_pitching = parse_stats(natstat_get('stats', 'npb', {'type':'player','stat':'era','season':SEASON}))
print(f"   {len(npb_pitching)} pitchers")
time.sleep(0.5)

print("→ NPB batting...")
npb_batting = parse_stats(natstat_get('stats', 'npb', {'type':'player','stat':'avg','season':SEASON}))
print(f"   {len(npb_batting)} batters")
time.sleep(0.5)

print("→ NPB team batting...")
npb_team_bat = parse_stats(natstat_get('stats', 'npb', {'type':'team','stat':'avg','season':SEASON}))
print(f"   {len(npb_team_bat)} teams")
time.sleep(0.5)

print("→ NPB team pitching...")
npb_team_pit = parse_stats(natstat_get('stats', 'npb', {'type':'team','stat':'era','season':SEASON}))
print(f"   {len(npb_team_pit)} teams")
time.sleep(0.5)

# ════════════════════════════════════════════════════════
# CBB (NCAA Baseball)
# ════════════════════════════════════════════════════════
print("\n→ CBB games today...")
cbb_today = parse_games(
    natstat_get('games', 'cbb', {'limit': 'today'}),
    TODAY.isoformat()
)
print(f"   {len(cbb_today)} games")
time.sleep(0.5)

print("→ CBB ELO + RPI...")
cbb_elo = parse_elo(natstat_get('elo', 'cbb', {'season': SEASON}))
print(f"   {len(cbb_elo)} teams")
time.sleep(0.5)

print("→ CBB pitching...")
cbb_raw = natstat_get('stats', 'cbb', {'type':'player','stat':'era','season':SEASON})
cbb_pitching = parse_stats(cbb_raw)
# Compute K/9, BB/9, FIP
for p in cbb_pitching:
    ip = float(p.get('ip') or 0)
    if ip > 0:
        k  = float(p.get('k') or p.get('so') or 0)
        bb = float(p.get('bb') or 0)
        hr = float(p.get('hr') or 0)
        if not p.get('k9'):  p['k9']  = round(k/ip*9, 2)
        if not p.get('bb9'): p['bb9'] = round(bb/ip*9, 2)
        if not p.get('fip'): p['fip'] = round((13*hr+3*bb-2*k)/ip+3.20, 2)
print(f"   {len(cbb_pitching)} pitchers")
time.sleep(0.5)

print("→ CBB batting...")
cbb_batting = parse_stats(natstat_get('stats', 'cbb', {'type':'player','stat':'avg','season':SEASON}))
for b in cbb_batting:
    obp = b.get('obp'); slg = b.get('slg')
    if obp and slg:
        try: b['ops'] = round(float(obp)+float(slg), 3)
        except: pass
print(f"   {len(cbb_batting)} batters")
time.sleep(0.5)

print("→ CBB team stats...")
cbb_team_bat = parse_stats(natstat_get('stats', 'cbb', {'type':'team','stat':'avg','season':SEASON}))
cbb_team_pit = parse_stats(natstat_get('stats', 'cbb', {'type':'team','stat':'era','season':SEASON}))
# Merge with ELO/RPI
cbb_team_stats = []
pit_map = {t['name'].lower(): t for t in cbb_team_pit if t.get('name')}
for t in cbb_team_bat:
    name = t.get('name','')
    pit  = pit_map.get(name.lower(), {})
    elo  = cbb_elo.get(name, {})
    rec  = dict(t)
    rec.update({'era': pit.get('era'), 'whip': pit.get('whip'),
                'rpi': elo.get('rpi'), 'elo':  elo.get('elo')})
    obp = rec.get('obp'); slg = rec.get('slg')
    if obp and slg:
        try: rec['ops'] = round(float(obp)+float(slg), 3)
        except: pass
    cbb_team_stats.append(rec)
print(f"   {len(cbb_team_stats)} teams")
time.sleep(0.5)

# ════════════════════════════════════════════════════════
# MLB ELO
# ════════════════════════════════════════════════════════
print("\n→ MLB ELO...")
mlb_elo = parse_elo(natstat_get('elo', 'mlb', {'season': SEASON}))
print(f"   {len(mlb_elo)} teams")

# ════════════════════════════════════════════════════════
# Output
# ════════════════════════════════════════════════════════
output = {
    "generated_at":       TODAY.isoformat(),
    "season":             SEASON,
    "npb_games_today":    npb_today,
    "npb_games_tomorrow": npb_tomorrow,
    "npb_elo":            npb_elo,
    "npb_pitching":       npb_pitching,
    "npb_batting":        npb_batting,
    "npb_team_batting":   npb_team_bat,
    "npb_team_pitching":  npb_team_pit,
    "cbb_games_today":    cbb_today,
    "cbb_elo":            cbb_elo,
    "cbb_pitching":       cbb_pitching,
    "cbb_batting":        cbb_batting,
    "cbb_team_stats":     cbb_team_stats,
    "mlb_elo":            mlb_elo,
}

with open("natstat_stats.json", "w", encoding="utf-8") as f:
    json.dump(output, f, separators=(",",":"))

size_kb = len(json.dumps(output)) / 1024
print(f"\n✅ natstat_stats.json — {size_kb:.1f} KB")
print(f"   NPB: {len(npb_today)} hoy | {len(npb_tomorrow)} mañana | {len(npb_pitching)} pitchers | {len(npb_batting)} bateadores")
print(f"   CBB: {len(cbb_today)} hoy | {len(cbb_pitching)} pitchers | {len(cbb_batting)} bateadores | {len(cbb_team_stats)} equipos")
print(f"   MLB ELO: {len(mlb_elo)} equipos")
