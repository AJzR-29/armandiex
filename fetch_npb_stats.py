"""
fetch_npb_stats.py
Genera npb_stats.json scrapeando npb.jp/bis/eng directamente.
Sin dependencias externas raras — solo requests + beautifulsoup4.
"""

import json, datetime, time
import requests
from bs4 import BeautifulSoup

TODAY  = datetime.date.today()
SEASON = TODAY.year
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

print(f"[fetch_npb_stats] {TODAY}  season={SEASON}")

def get(url, delay=1.5):
    try:
        time.sleep(delay)
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f"  WARNING GET {url} -> {e}")
        return None

def safe(val):
    try:
        if val is None or val == '' or val == '-': return None
        return round(float(str(val).replace(',','')), 3)
    except: return str(val).strip() if val else None

def parse_table(soup, label):
    if not soup: return []
    table = soup.find('table')
    if not table: return []
    rows = table.find_all('tr')
    if not rows: return []
    headers = [th.get_text(strip=True) for th in rows[0].find_all(['th','td'])]
    records = []
    for row in rows[1:]:
        cells = [td.get_text(strip=True) for td in row.find_all('td')]
        if not cells or len(cells) < 3: continue
        rec = {}
        for i, h in enumerate(headers):
            if i < len(cells) and h:
                rec[h] = safe(cells[i]) if i > 1 else cells[i]
        if rec: records.append(rec)
    print(f"  OK {label}: {len(records)} rows")
    return records

BASE = f"https://npb.jp/bis/eng/{SEASON}"

# Individual batting
print("-> Individual batting...")
npb_batting = []
for lg in ['c','p']:
    soup = get(f"{BASE}/stats/bat_{lg}.html")
    rows = parse_table(soup, f"bat_{lg}")
    for r in rows: r['League'] = 'CL' if lg=='c' else 'PL'
    npb_batting.extend(rows)
if not npb_batting:
    soup = get(f"{BASE}/stats/idp_b.html")
    npb_batting = parse_table(soup, "idp_b")

# Individual pitching
print("-> Individual pitching...")
npb_pitching = []
for lg in ['c','p']:
    soup = get(f"{BASE}/stats/pit_{lg}.html")
    rows = parse_table(soup, f"pit_{lg}")
    for r in rows: r['League'] = 'CL' if lg=='c' else 'PL'
    npb_pitching.extend(rows)
if not npb_pitching:
    soup = get(f"{BASE}/stats/idp_p.html")
    npb_pitching = parse_table(soup, "idp_p")

# Team stats
print("-> Team stats...")
npb_team_batting, npb_team_pitching = [], []
for lg in ['c','p']:
    soup = get(f"{BASE}/stats/tm_bat_{lg}.html")
    rows = parse_table(soup, f"tm_bat_{lg}")
    for r in rows: r['League'] = 'CL' if lg=='c' else 'PL'
    npb_team_batting.extend(rows)
    soup = get(f"{BASE}/stats/tm_pit_{lg}.html")
    rows = parse_table(soup, f"tm_pit_{lg}")
    for r in rows: r['League'] = 'CL' if lg=='c' else 'PL'
    npb_team_pitching.extend(rows)

# Standings
print("-> Standings...")
npb_standings = []
for lg in ['cl','pl']:
    soup = get(f"https://npb.jp/bis/eng/{SEASON}/standings/{lg}standings.html")
    rows = parse_table(soup, f"{lg}standings")
    for r in rows: r['League'] = lg.upper()
    npb_standings.extend(rows)

# Probable pitchers
print("-> Probable pitchers...")
probable_pitchers = {}
date_str = TODAY.strftime("%Y%m%d")
soup = get(f"{BASE}/calendar/{date_str}.html", delay=2)
if soup:
    table = soup.find('table')
    if table:
        for row in table.find_all('tr')[1:]:
            cells = [td.get_text(strip=True) for td in row.find_all('td')]
            if len(cells) >= 2:
                home   = cells[0] or None
                away   = cells[1] if len(cells)>1 else None
                hpitch = cells[2] if len(cells)>2 else 'TBD'
                apitch = cells[3] if len(cells)>3 else 'TBD'
                if home: probable_pitchers[home] = {'pitcher': hpitch or 'TBD', 'isHome': True}
                if away: probable_pitchers[away] = {'pitcher': apitch or 'TBD', 'isHome': False}
print(f"  probable_pitchers: {len(probable_pitchers)}")

# Compute K/9, BB/9, FIP where missing
for p in npb_pitching:
    try:
        ip = float(str(p.get('IP',0) or 0))
        if ip > 0:
            k  = float(str(p.get('SO', p.get('K',0)) or 0))
            bb = float(str(p.get('BB',0) or 0))
            hr = float(str(p.get('HR',0) or 0))
            if not p.get('K/9'):  p['K/9']  = round(k/ip*9, 2)
            if not p.get('BB/9'): p['BB/9'] = round(bb/ip*9, 2)
            if not p.get('FIP'):  p['FIP']  = round((13*hr+3*bb-2*k)/ip+3.20, 2)
    except: pass

output = {
    "generated_at":          TODAY.isoformat(),
    "season":                SEASON,
    "npb_batting":           npb_batting,
    "npb_pitching":          npb_pitching,
    "npb_team_batting":      npb_team_batting,
    "npb_team_pitching":     npb_team_pitching,
    "npb_standings":         npb_standings,
    "npb_probable_pitchers": probable_pitchers,
}

with open("npb_stats.json", "w", encoding="utf-8") as f:
    json.dump(output, f, separators=(",",":"), ensure_ascii=False)

size_kb = len(json.dumps(output, ensure_ascii=False)) / 1024
print(f"\nOK npb_stats.json -- {size_kb:.1f} KB")
print(f"   batting:{len(npb_batting)} pitching:{len(npb_pitching)}")
print(f"   team_bat:{len(npb_team_batting)} team_pit:{len(npb_team_pitching)}")
print(f"   standings:{len(npb_standings)} probable:{len(probable_pitchers)}")
