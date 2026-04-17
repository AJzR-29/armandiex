"""
fetch_ncaa_stats.py v2
Scrape stats.ncaa.org directamente — sin depender de collegebaseball
Genera ncaa_stats.json con pitching, batting y team stats
"""
import json, datetime, time, requests
from bs4 import BeautifulSoup

TODAY  = datetime.date.today()
SEASON = TODAY.year
print(f"[fetch_ncaa_stats v2] {TODAY} season={SEASON}")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}

def get(url, delay=2):
    try:
        time.sleep(delay)
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        print(f"  OK {url[:80]} ({r.status_code})")
        return BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f"  WARN {url[:80]} -> {e}")
        return None

def safe(val):
    try:
        if val is None or str(val).strip() in ('', '-', '---', 'nan'): return None
        return round(float(str(val).replace(',', '')), 3)
    except: return str(val).strip() if val else None

def parse_ncaa_table(soup, label):
    if not soup: return []
    table = soup.find('table', id='rankings_table') or soup.find('table')
    if not table: return []
    rows = table.find_all('tr')
    if len(rows) < 2: return []
    headers = [th.get_text(strip=True) for th in rows[0].find_all(['th','td'])]
    records = []
    for row in rows[1:]:
        cells = [td.get_text(strip=True) for td in row.find_all('td')]
        if not cells or len(cells) < 3: continue
        rec = {}
        for i, h in enumerate(headers):
            if i < len(cells) and h:
                rec[h] = cells[i]
        if rec: records.append(rec)
    print(f"  {label}: {len(records)} rows")
    return records

# ═══════════════════════════════════════════════════════
# NCAA stats.ncaa.org — stat_seq codes for 2026
# ERA=139, WHIP=473, K=148, BB=147, W=141, IP=155
# AVG=125, OBP=127, SLG=128, HR=132, RBI=131, BB=130
# ═══════════════════════════════════════════════════════

BASE = "https://stats.ncaa.org/rankings/national_ranking"
SPORT = "MBA"  # Men's Baseball
DIV = "1.0"

# Academic year format for NCAA
ACAD_YEAR = f"{SEASON}.0"
# Ranking period: 1=full season, others=weekly
PERIOD = "1.0"

ncaa_pitching   = []
ncaa_batting    = []
ncaa_team_stats = []

# ── 1. Pitching — ERA leaders ─────────────────────────────────
print("→ NCAA pitching (ERA)...")
url = f"{BASE}?academic_year={ACAD_YEAR}&division={DIV}&ranking_period={PERIOD}&sport_code={SPORT}&stat_seq=139.0"
soup = get(url, delay=2)
if soup:
    rows = parse_ncaa_table(soup, "ERA leaders")
    for r in rows:
        rec = {
            'name':  r.get('Player','') or r.get('Name',''),
            'team':  r.get('Team','') or r.get('School',''),
            'era':   safe(r.get('ERA','')),
            'ip':    safe(r.get('IP','')),
            'w':     safe(r.get('W','')),
            'l':     safe(r.get('L','')),
            'g':     safe(r.get('G','')),
        }
        if rec['name']: ncaa_pitching.append(rec)

# ── 2. Pitching — K leaders (merge into existing) ───────────────
print("→ NCAA pitching (K/9)...")
url = f"{BASE}?academic_year={ACAD_YEAR}&division={DIV}&ranking_period={PERIOD}&sport_code={SPORT}&stat_seq=148.0"
soup = get(url, delay=2)
k_map = {}
if soup:
    rows = parse_ncaa_table(soup, "K leaders")
    for r in rows:
        name = r.get('Player','') or r.get('Name','')
        team = r.get('Team','') or r.get('School','')
        if name:
            k_map[f"{name}_{team}"] = {
                'k':   safe(r.get('SO',r.get('K',''))),
                'bb':  safe(r.get('BB','')),
            }

# Merge K data into pitching
for p in ncaa_pitching:
    key = f"{p['name']}_{p['team']}"
    if key in k_map:
        p.update(k_map[key])
    # Compute K/9 and BB/9
    if p.get('ip') and p['ip'] > 0:
        if p.get('k'):
            p['k9'] = round(float(p['k']) / p['ip'] * 9, 2)
        if p.get('bb'):
            p['bb9'] = round(float(p['bb']) / p['ip'] * 9, 2)
        # Compute FIP approximation
        hr = float(p.get('hr', 0) or 0)
        bb = float(p.get('bb', 0) or 0)
        k  = float(p.get('k', 0) or 0)
        ip = float(p['ip'])
        if ip > 0:
            p['fip'] = round((13*hr + 3*bb - 2*k) / ip + 3.20, 2)

print(f"  total pitchers: {len(ncaa_pitching)}")

# ── 3. Batting — AVG leaders ────────────────────────────────────
print("→ NCAA batting (AVG)...")
url = f"{BASE}?academic_year={ACAD_YEAR}&division={DIV}&ranking_period={PERIOD}&sport_code={SPORT}&stat_seq=125.0"
soup = get(url, delay=2)
if soup:
    rows = parse_ncaa_table(soup, "AVG leaders")
    for r in rows:
        rec = {
            'name': r.get('Player','') or r.get('Name',''),
            'team': r.get('Team','') or r.get('School',''),
            'avg':  safe(r.get('BA', r.get('AVG',''))),
            'ab':   safe(r.get('AB','')),
            'h':    safe(r.get('H','')),
            'hr':   safe(r.get('HR','')),
            'rbi':  safe(r.get('RBI','')),
            'r':    safe(r.get('R','')),
            'bb':   safe(r.get('BB','')),
            'g':    safe(r.get('G','')),
        }
        if rec['name']: ncaa_batting.append(rec)

# ── 4. Batting — OBP leaders ────────────────────────────────────
print("→ NCAA batting (OBP)...")
url = f"{BASE}?academic_year={ACAD_YEAR}&division={DIV}&ranking_period={PERIOD}&sport_code={SPORT}&stat_seq=127.0"
soup = get(url, delay=2)
obp_map = {}
if soup:
    rows = parse_ncaa_table(soup, "OBP leaders")
    for r in rows:
        name = r.get('Player','') or r.get('Name','')
        team = r.get('Team','') or r.get('School','')
        if name:
            obp_map[f"{name}_{team}"] = {
                'obp': safe(r.get('OBPct', r.get('OBP',''))),
                'slg': safe(r.get('SlgPct', r.get('SLG',''))),
            }

# Merge OBP/SLG into batting
for b in ncaa_batting:
    key = f"{b['name']}_{b['team']}"
    if key in obp_map:
        b.update(obp_map[key])
    if b.get('obp') and b.get('slg'):
        try:
            b['ops'] = round(float(b['obp']) + float(b['slg']), 3)
        except: pass

print(f"  total batters: {len(ncaa_batting)}")

# ── 5. Team stats — aggregate by team ───────────────────────────
print("→ NCAA team stats...")
team_pit_map = {}
team_bat_map = {}

# Team ERA
url = f"{BASE}?academic_year={ACAD_YEAR}&division={DIV}&ranking_period={PERIOD}&sport_code={SPORT}&stat_seq=139.0&team_individual=T"
soup = get(url, delay=2)
if soup:
    rows = parse_ncaa_table(soup, "team ERA")
    for r in rows:
        team = r.get('Team','') or r.get('Name','')
        if team:
            team_pit_map[team] = {
                'team': team,
                'era':  safe(r.get('ERA','')),
                'whip': safe(r.get('WHIP','')),
            }

# Team AVG
url = f"{BASE}?academic_year={ACAD_YEAR}&division={DIV}&ranking_period={PERIOD}&sport_code={SPORT}&stat_seq=125.0&team_individual=T"
soup = get(url, delay=2)
if soup:
    rows = parse_ncaa_table(soup, "team AVG")
    for r in rows:
        team = r.get('Team','') or r.get('Name','')
        if team:
            team_bat_map[team] = {
                'team': team,
                'avg':  safe(r.get('BA', r.get('AVG',''))),
                'obp':  safe(r.get('OBPct', r.get('OBP',''))),
                'slg':  safe(r.get('SlgPct', r.get('SLG',''))),
            }

# Merge team stats
all_teams = set(list(team_pit_map.keys()) + list(team_bat_map.keys()))
for team in all_teams:
    rec = {'team': team}
    if team in team_pit_map: rec.update(team_pit_map[team])
    if team in team_bat_map: rec.update(team_bat_map[team])
    if rec.get('obp') and rec.get('slg'):
        try: rec['ops'] = round(float(rec['obp']) + float(rec['slg']), 3)
        except: pass
    ncaa_team_stats.append(rec)

print(f"  total teams: {len(ncaa_team_stats)}")

# ── 6. Output ─────────────────────────────────────────────────────
output = {
    "generated_at": TODAY.isoformat(),
    "season":       SEASON,
    "pitching":     ncaa_pitching,
    "batting":      ncaa_batting,
    "team_stats":   ncaa_team_stats,
}

with open("ncaa_stats.json", "w", encoding="utf-8") as f:
    json.dump(output, f, separators=(",",":"))

size_kb = len(json.dumps(output)) / 1024
print(f"\n✅ ncaa_stats.json — {size_kb:.1f} KB")
print(f"   pitching:{len(ncaa_pitching)} batting:{len(ncaa_batting)} teams:{len(ncaa_team_stats)}")
