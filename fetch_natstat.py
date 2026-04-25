"""
fetch_natstat.py v3
API v4: https://api4.natst.at/{key}/{endpoint}/{service}/{range_params}
Range params are comma-separated PATH values, not query params
"""

import json, datetime, time, math, requests

TODAY    = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
SEASON   = TODAY.year
KEY      = "74db-1689d0"
BASE     = f"https://api4.natst.at/{KEY}"

print(f"[fetch_natstat v3] {TODAY} season={SEASON}")

def safe(val):
    try:
        if val is None: return None
        f = float(str(val).replace('%','').strip())
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 3)
    except: return str(val).strip() if val else None

def natstat_get(endpoint, service, range_params='', extra_params={}):
    """
    v4 URL format: /key/endpoint/SERVICE/range_params
    Service code must be UPPERCASE (NPB, CBB, MLB)
    Range params are comma-separated path values
    """
    svc = service.upper()  # API requires uppercase
    url = f"{BASE}/{endpoint}/{svc}/"
    if range_params:
        url += f"{range_params}/"
    p = {'dataformat': 'json'}
    p.update(extra_params)
    try:
        r = requests.get(url, params=p, timeout=15)
        print(f"  {r.status_code} {svc}/{endpoint}/{range_params or '_'}")
        if r.status_code == 500:
            # Try without range params as query param instead
            url2 = f"{BASE}/{endpoint}/{svc}/"
            p2 = dict(p)
            if range_params:
                parts = range_params.split(',')
                for i, part in enumerate(parts):
                    if part.isdigit(): p2['season'] = part
                    elif '-' in part and len(part)==10: p2['date'] = part
                    elif part in ('player','team'): p2['type'] = part
                    else: p2['stat'] = part
            r2 = requests.get(url2, params=p2, timeout=15)
            print(f"  {r2.status_code} retry as query params → {url2}")
            if r2.status_code < 400:
                r = r2
            else:
                print(f"    Both failed. Response: {r.text[:100]}")
                return None
        elif r.status_code >= 400:
            print(f"    Error: {r.text[:200]}")
            return None
        data = r.json()
        if isinstance(data, dict) and data.get('success') == 0:
            print(f"    API error: {data.get('error',{})}")
            return None
        return data
    except Exception as e:
        print(f"  WARN {service}/{endpoint}: {e}")
        return None

def get_records(data, keys):
    """Extract records from various response structures"""
    if not data: return []
    for key in keys:
        val = data.get(key)
        if val:
            if isinstance(val, dict): return list(val.values())
            if isinstance(val, list): return val
    return []

def parse_games(data, date_str):
    games = []
    records = get_records(data, ['games','data','results','items'])
    for g in records:
        if not isinstance(g, dict): continue
        home = (g.get('home_team_name') or g.get('home_name') or g.get('home') or g.get('hteam',''))
        away = (g.get('away_team_name') or g.get('away_name') or g.get('away') or g.get('ateam',''))
        if not home: continue
        games.append({
            'game_id':  str(g.get('id') or g.get('game_id','')),
            'home':     home, 'away': away,
            'home_id':  g.get('home_team_id') or g.get('home_id',''),
            'away_id':  g.get('away_team_id') or g.get('away_id',''),
            'date':     g.get('date', date_str),
            'time':     g.get('time') or g.get('game_time',''),
            'status':   g.get('status',''),
            'hPitcher': g.get('home_probable_pitcher') or g.get('hpitcher','TBD') or 'TBD',
            'aPitcher': g.get('away_probable_pitcher') or g.get('apitcher','TBD') or 'TBD',
        })
    return games

def parse_stats(data):
    records = []
    items = get_records(data, ['stats','players','teams','data','results'])
    for p in items:
        if not isinstance(p, dict): continue
        name = (p.get('player_name') or p.get('name') or p.get('player') or
                p.get('team_name') or p.get('team',''))
        team = p.get('team_name') or p.get('team','')
        rec  = {'name': name, 'team': team}
        for f in p:
            v = p[f]
            if v is not None and isinstance(v, (int, float, str)):
                rec[f.lower()] = safe(v) if f.lower() not in ('name','team','player_name','team_name') else str(v)
        if name: records.append(rec)
    return records

def parse_elo(data):
    result = {}
    items = get_records(data, ['elo','teams','data','results'])
    for e in items:
        if not isinstance(e, dict): continue
        team = e.get('team_name') or e.get('team') or e.get('name','')
        if team:
            result[team] = {
                'elo':      safe(e.get('elo') or e.get('rating') or e.get('elo_rating')),
                'win_prob': safe(e.get('win_prob') or e.get('winprob') or e.get('prob')),
                'rpi':      safe(e.get('rpi')),
            }
    return result

def parse_forecasts(data):
    """Parse win probability / forecast data"""
    result = []
    items = get_records(data, ['forecasts','games','data','results'])
    for f in items:
        if not isinstance(f, dict): continue
        result.append({
            'game_id':   f.get('id') or f.get('game_id',''),
            'home':      f.get('home_team_name') or f.get('home',''),
            'away':      f.get('away_team_name') or f.get('away',''),
            'home_prob': safe(f.get('home_prob') or f.get('win_prob_home') or f.get('elo_home')),
            'away_prob': safe(f.get('away_prob') or f.get('win_prob_away') or f.get('elo_away')),
            'home_ml':   safe(f.get('home_ml') or f.get('moneyline_home')),
            'away_ml':   safe(f.get('away_ml') or f.get('moneyline_away')),
            'over_under':safe(f.get('over_under') or f.get('total')),
            'date':      f.get('date',''),
        })
    return result

# ════════════════════════════════════════════════════════
# NPB
# ════════════════════════════════════════════════════════
print("\n→ NPB games today...")
npb_today = parse_games(
    natstat_get('games', 'npb', TODAY.strftime('%Y-%m-%d')),
    TODAY.isoformat()
)
print(f"   {len(npb_today)} games")
time.sleep(0.4)

print("→ NPB games tomorrow...")
npb_tomorrow = parse_games(
    natstat_get('games', 'npb', TOMORROW.strftime('%Y-%m-%d')),
    TOMORROW.isoformat()
)
print(f"   {len(npb_tomorrow)} games")
time.sleep(0.4)

print("→ NPB forecasts today (win prob + moneyline)...")
npb_forecasts = parse_forecasts(
    natstat_get('forecasts', 'npb', TODAY.strftime('%Y-%m-%d'))
)
print(f"   {len(npb_forecasts)} forecasts")
time.sleep(0.4)

print("→ NPB ELO...")
npb_elo = parse_elo(natstat_get('elo', 'npb', str(SEASON)))
print(f"   {len(npb_elo)} teams")
time.sleep(0.4)

print("→ NPB pitching (ERA, season)...")
npb_pitching = parse_stats(natstat_get('stats', 'npb', f"{SEASON},era,player"))
print(f"   {len(npb_pitching)} pitchers")
time.sleep(0.4)

print("→ NPB batting (AVG, season)...")
npb_batting = parse_stats(natstat_get('stats', 'npb', f"{SEASON},avg,player"))
print(f"   {len(npb_batting)} batters")
time.sleep(0.4)

print("→ NPB team batting...")
npb_team_bat = parse_stats(natstat_get('stats', 'npb', f"{SEASON},avg,team"))
print(f"   {len(npb_team_bat)} teams")
time.sleep(0.4)

print("→ NPB team pitching...")
npb_team_pit = parse_stats(natstat_get('stats', 'npb', f"{SEASON},era,team"))
print(f"   {len(npb_team_pit)} teams")
time.sleep(0.4)

# ════════════════════════════════════════════════════════
# CBB (NCAA Baseball)
# ════════════════════════════════════════════════════════
print("\n→ CBB games today...")
cbb_today = parse_games(
    natstat_get('games', 'cbb', TODAY.strftime('%Y-%m-%d')),
    TODAY.isoformat()
)
print(f"   {len(cbb_today)} games")
time.sleep(0.4)

print("→ CBB forecasts today...")
cbb_forecasts = parse_forecasts(
    natstat_get('forecasts', 'cbb', TODAY.strftime('%Y-%m-%d'))
)
print(f"   {len(cbb_forecasts)} forecasts")
time.sleep(0.4)

print("→ CBB ELO + RPI...")
cbb_elo = parse_elo(natstat_get('elo', 'cbb', str(SEASON)))
print(f"   {len(cbb_elo)} teams")
time.sleep(0.4)

print("→ CBB pitching...")
cbb_pitching = parse_stats(natstat_get('stats', 'cbb', f"{SEASON},era,player"))
# Compute derived stats
for p in cbb_pitching:
    ip = float(p.get('ip') or 0)
    if ip > 0:
        k  = float(p.get('so') or p.get('k') or 0)
        bb = float(p.get('bb') or 0)
        hr = float(p.get('hr') or 0)
        if not p.get('k9'):  p['k9']  = round(k/ip*9, 2)
        if not p.get('bb9'): p['bb9'] = round(bb/ip*9, 2)
        if not p.get('fip'): p['fip'] = round((13*hr+3*bb-2*k)/ip+3.20, 2)
print(f"   {len(cbb_pitching)} pitchers")
time.sleep(0.4)

print("→ CBB batting...")
cbb_batting = parse_stats(natstat_get('stats', 'cbb', f"{SEASON},avg,player"))
for b in cbb_batting:
    obp = b.get('obp'); slg = b.get('slg')
    if obp and slg:
        try: b['ops'] = round(float(obp)+float(slg), 3)
        except: pass
print(f"   {len(cbb_batting)} batters")
time.sleep(0.4)

print("→ CBB team stats...")
cbb_team_bat = parse_stats(natstat_get('stats', 'cbb', f"{SEASON},avg,team"))
cbb_team_pit = parse_stats(natstat_get('stats', 'cbb', f"{SEASON},era,team"))
cbb_team_stats = []
pit_map = {t.get('name','').lower(): t for t in cbb_team_pit}
for t in cbb_team_bat:
    name = t.get('name','')
    pit  = pit_map.get(name.lower(), {})
    elo  = cbb_elo.get(name, {})
    rec  = dict(t)
    rec.update({'era':pit.get('era'),'whip':pit.get('whip'),
                'rpi':elo.get('rpi'),'elo':elo.get('elo')})
    obp = rec.get('obp'); slg = rec.get('slg')
    if obp and slg:
        try: rec['ops'] = round(float(obp)+float(slg), 3)
        except: pass
    cbb_team_stats.append(rec)
print(f"   {len(cbb_team_stats)} teams")
time.sleep(0.4)

# ════════════════════════════════════════════════════════
# MLB
# ════════════════════════════════════════════════════════
print("\n→ MLB ELO...")
mlb_elo = parse_elo(natstat_get('elo', 'mlb', str(SEASON)))
print(f"   {len(mlb_elo)} teams")
time.sleep(0.4)

print("→ MLB forecasts today...")
mlb_forecasts = parse_forecasts(
    natstat_get('forecasts', 'mlb', TODAY.strftime('%Y-%m-%d'))
)
print(f"   {len(mlb_forecasts)} forecasts")
time.sleep(0.4)

print("→ MLB moneyline today...")
mlb_moneyline = parse_forecasts(
    natstat_get('moneyline', 'mlb', TODAY.strftime('%Y-%m-%d'))
)
print(f"   {len(mlb_moneyline)} lines")

# ════════════════════════════════════════════════════════
# Output
# ════════════════════════════════════════════════════════
output = {
    "generated_at":       TODAY.isoformat(),
    "season":             SEASON,
    "npb_games_today":    npb_today,
    "npb_games_tomorrow": npb_tomorrow,
    "npb_forecasts":      npb_forecasts,
    "npb_elo":            npb_elo,
    "npb_pitching":       npb_pitching,
    "npb_batting":        npb_batting,
    "npb_team_batting":   npb_team_bat,
    "npb_team_pitching":  npb_team_pit,
    "cbb_games_today":    cbb_today,
    "cbb_forecasts":      cbb_forecasts,
    "cbb_elo":            cbb_elo,
    "cbb_pitching":       cbb_pitching,
    "cbb_batting":        cbb_batting,
    "cbb_team_stats":     cbb_team_stats,
    "mlb_elo":            mlb_elo,
    "mlb_forecasts":      mlb_forecasts,
    "mlb_moneyline":      mlb_moneyline,
}

with open("natstat_stats.json", "w", encoding="utf-8") as f:
    json.dump(output, f, separators=(",",":"))

size_kb = len(json.dumps(output)) / 1024
print(f"\n✅ natstat_stats.json v3 — {size_kb:.1f} KB")
print(f"   NPB: {len(npb_today)} hoy | {len(npb_tomorrow)} mañana | {len(npb_forecasts)} forecasts | {len(npb_pitching)} pitchers")
print(f"   CBB: {len(cbb_today)} hoy | {len(cbb_forecasts)} forecasts | {len(cbb_pitching)} pitchers | {len(cbb_batting)} bateadores")
print(f"   MLB: {len(mlb_elo)} ELO | {len(mlb_forecasts)} forecasts | {len(mlb_moneyline)} moneylines")
