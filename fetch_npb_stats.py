"""
fetch_npb_stats.py - Genera npb_stats.json
Fuente principal: npb.jp/bis/eng/2026/games/ (schedule oficial)
"""

import json, datetime, time
import requests
from bs4 import BeautifulSoup

TODAY    = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
SEASON   = TODAY.year
HEADERS  = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

print(f"[fetch_npb_stats] {TODAY} season={SEASON}")

def get(url, delay=2):
    try:
        time.sleep(delay)
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        print(f"  OK {url} ({r.status_code})")
        return BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f"  WARN {url} -> {e}")
        return None

def safe(val):
    try:
        if val is None or str(val).strip() in ('', '-', '---'): return None
        return round(float(str(val).replace(',', '')), 3)
    except: return str(val).strip() if val else None

def parse_table(soup, label):
    if not soup: return []
    table = soup.find('table')
    if not table: return []
    rows = table.find_all('tr')
    if len(rows) < 2: return []
    headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
    records = []
    for row in rows[1:]:
        cells = [td.get_text(strip=True) for td in row.find_all('td')]
        if not cells or len(cells) < 3: continue
        rec = {}
        for i, h in enumerate(headers):
            if i < len(cells) and h:
                rec[h] = safe(cells[i]) if i > 1 else cells[i]
        if rec: records.append(rec)
    print(f"  {label}: {len(records)} rows")
    return records

BASE = f"https://npb.jp/bis/eng/{SEASON}"

# ═══════════════════════════════════════════════════
# 1. PARSE GAMES FROM npb.jp/bis/eng/2026/games/
# Returns: [{home, away, hPitcher, aPitcher, time, date}]
# ═══════════════════════════════════════════════════
def parse_games_page(date):
    """Parse the npb.jp games page for a given date."""
    # npb.jp uses ?date=YYYYMMDD or just shows current day
    date_str = date.strftime("%Y%m%d")
    games = []

    # Try the games page with date param
    urls_to_try = [
        f"{BASE}/games/{date_str}_games.html",
        f"https://npb.jp/bis/eng/{SEASON}/games/",
        f"https://npb.jp/bis/eng/games/",
    ]

    soup = None
    for url in urls_to_try:
        soup = get(url, delay=1.5)
        if soup and soup.find('table'):
            break

    if not soup:
        return games

    # Find all game tables — each game is usually in a table or div
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all('td')]
            if len(cells) >= 2:
                # Look for team vs team pattern
                home = cells[0].strip() if cells[0] else ''
                away = cells[1].strip() if len(cells) > 1 else ''
                hpitch = cells[2].strip() if len(cells) > 2 else 'TBD'
                apitch = cells[3].strip() if len(cells) > 3 else 'TBD'
                gtime  = cells[4].strip() if len(cells) > 4 else ''
                if home and away and len(home) > 2 and len(away) > 2:
                    games.append({
                        'home': home, 'away': away,
                        'hPitcher': hpitch or 'TBD',
                        'aPitcher': apitch or 'TBD',
                        'time': gtime,
                        'date': date.isoformat()
                    })

    return games

# ═══════════════════════════════════════════════════
# 2. HARDCODE TODAY'S GAMES from search results
#    (fallback when scraping fails)
# ═══════════════════════════════════════════════════
def get_hardcoded_games(date):
    """
    Hardcoded schedule as fallback.
    Manually update if scraping fails.
    Games on 2026-04-14 and 2026-04-15 from livesport.com
    """
    SCHEDULE = {
        "2026-04-14": [
            {"home": "Yokohama BayStars",          "away": "Yakult Swallows",         "hPitcher": "TBD", "aPitcher": "TBD"},
            {"home": "Hiroshima Toyo Carp",         "away": "Chunichi Dragons",        "hPitcher": "TBD", "aPitcher": "TBD"},
            {"home": "Yomiuri Giants",              "away": "Hanshin Tigers",          "hPitcher": "TBD", "aPitcher": "TBD"},
            {"home": "Nippon-Ham Fighters",         "away": "Lotte Marines",           "hPitcher": "TBD", "aPitcher": "TBD"},
            {"home": "Seibu Lions",                 "away": "Orix Buffaloes",          "hPitcher": "TBD", "aPitcher": "TBD"},
            {"home": "Rakuten Eagles",              "away": "Fukuoka SoftBank Hawks",  "hPitcher": "TBD", "aPitcher": "TBD"},
        ],
        "2026-04-15": [
            {"home": "Hiroshima Toyo Carp",         "away": "Chunichi Dragons",        "hPitcher": "TBD", "aPitcher": "TBD"},
            {"home": "Yomiuri Giants",              "away": "Hanshin Tigers",          "hPitcher": "TBD", "aPitcher": "TBD"},
            {"home": "Nippon-Ham Fighters",         "away": "Lotte Marines",           "hPitcher": "TBD", "aPitcher": "TBD"},
            {"home": "Seibu Lions",                 "away": "Orix Buffaloes",          "hPitcher": "TBD", "aPitcher": "TBD"},
            {"home": "Rakuten Eagles",              "away": "Fukuoka SoftBank Hawks",  "hPitcher": "TBD", "aPitcher": "TBD"},
        ],
    }
    date_str = date.isoformat()
    games = SCHEDULE.get(date_str, [])
    for g in games: g['date'] = date_str
    return games

# ═══════════════════════════════════════════════════
# 3. FETCH PROBABLE PITCHERS from npb.jp/announcement/starter
# ═══════════════════════════════════════════════════
def fetch_probable_pitchers():
    """Scrape npb.jp starter announcements."""
    pitchers = {}
    try:
        # Try English games page which sometimes has pitchers
        soup = get(f"{BASE}/games/", delay=2)
        if not soup: return pitchers

        # Look for pitcher info in any table
        for table in (soup.find_all('table') or []):
            rows = table.find_all('tr')
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 4:
                    home = cells[0].strip()
                    away = cells[1].strip()
                    hp   = cells[2].strip()
                    ap   = cells[3].strip()
                    if home and hp and hp not in ('', '-', 'TBD'):
                        pitchers[home] = hp
                    if away and ap and ap not in ('', '-', 'TBD'):
                        pitchers[away] = ap
    except Exception as e:
        print(f"  probable pitchers error: {e}")
    return pitchers

# ═══════════════════════════════════════════════════
# 4. INDIVIDUAL BATTING STATS
# ═══════════════════════════════════════════════════
print("-> Batting stats...")
npb_batting = []
for lg in ['c', 'p']:
    soup = get(f"{BASE}/stats/bat_{lg}.html")
    rows = parse_table(soup, f"bat_{lg}")
    for r in rows: r['League'] = 'CL' if lg == 'c' else 'PL'
    npb_batting.extend(rows)

# ═══════════════════════════════════════════════════
# 5. INDIVIDUAL PITCHING STATS
# ═══════════════════════════════════════════════════
print("-> Pitching stats...")
npb_pitching = []
for lg in ['c', 'p']:
    soup = get(f"{BASE}/stats/pit_{lg}.html")
    rows = parse_table(soup, f"pit_{lg}")
    for r in rows: r['League'] = 'CL' if lg == 'c' else 'PL'
    npb_pitching.extend(rows)

# Compute K/9 BB/9 FIP where missing
for p in npb_pitching:
    try:
        ip = float(str(p.get('IP', 0) or 0))
        if ip > 0:
            k  = float(str(p.get('SO', p.get('K', 0)) or 0))
            bb = float(str(p.get('BB', 0) or 0))
            hr = float(str(p.get('HR', 0) or 0))
            if not p.get('K/9'):  p['K/9']  = round(k / ip * 9, 2)
            if not p.get('BB/9'): p['BB/9'] = round(bb / ip * 9, 2)
            if not p.get('FIP'):  p['FIP']  = round((13*hr + 3*bb - 2*k) / ip + 3.20, 2)
    except: pass

# ═══════════════════════════════════════════════════
# 6. TEAM BATTING & PITCHING
# ═══════════════════════════════════════════════════
print("-> Team stats...")
npb_team_batting, npb_team_pitching = [], []
for lg in ['c', 'p']:
    soup = get(f"{BASE}/stats/tm_bat_{lg}.html")
    rows = parse_table(soup, f"tm_bat_{lg}")
    for r in rows: r['League'] = 'CL' if lg == 'c' else 'PL'
    npb_team_batting.extend(rows)

    soup = get(f"{BASE}/stats/tm_pit_{lg}.html")
    rows = parse_table(soup, f"tm_pit_{lg}")
    for r in rows: r['League'] = 'CL' if lg == 'c' else 'PL'
    npb_team_pitching.extend(rows)

# ═══════════════════════════════════════════════════
# 7. STANDINGS
# ═══════════════════════════════════════════════════
print("-> Standings...")
npb_standings = []
for lg in ['cl', 'pl']:
    soup = get(f"{BASE}/standings/{lg}standings.html")
    rows = parse_table(soup, f"{lg}standings")
    for r in rows: r['League'] = lg.upper()
    npb_standings.extend(rows)

# ═══════════════════════════════════════════════════
# 8. GAMES TODAY & TOMORROW
# ═══════════════════════════════════════════════════
print("-> Games schedule...")

# Try scraping first, fallback to hardcoded
today_games = parse_games_page(TODAY)
if not today_games:
    print("  scraping failed, using hardcoded schedule")
    today_games = get_hardcoded_games(TODAY)

tomorrow_games = parse_games_page(TOMORROW)
if not tomorrow_games:
    tomorrow_games = get_hardcoded_games(TOMORROW)

# Try to get pitcher names
probable = fetch_probable_pitchers()
for g in today_games + tomorrow_games:
    if g.get('hPitcher', 'TBD') == 'TBD' and g['home'] in probable:
        g['hPitcher'] = probable[g['home']]
    if g.get('aPitcher', 'TBD') == 'TBD' and g['away'] in probable:
        g['aPitcher'] = probable[g['away']]

print(f"  today: {len(today_games)} games | tomorrow: {len(tomorrow_games)} games")

# ═══════════════════════════════════════════════════
# 9. OUTPUT
# ═══════════════════════════════════════════════════

# Convert games to probable_pitchers format for app compatibility
def games_to_probable(games):
    result = {}
    for g in games:
        if g.get('home') and g['home'] != '—':
            result[g['home']] = {'pitcher': g.get('hPitcher', 'TBD'), 'isHome': True,  'away': g.get('away', ''), 'date': g.get('date', '')}
        if g.get('away') and g['away'] != '—':
            result[g['away']] = {'pitcher': g.get('aPitcher', 'TBD'), 'isHome': False, 'home': g.get('home', ''), 'date': g.get('date', '')}
    return result

output = {
    "generated_at":           TODAY.isoformat(),
    "season":                 SEASON,
    "npb_batting":            npb_batting,
    "npb_pitching":           npb_pitching,
    "npb_team_batting":       npb_team_batting,
    "npb_team_pitching":      npb_team_pitching,
    "npb_standings":          npb_standings,
    "npb_games_today":        today_games,
    "npb_games_tomorrow":     tomorrow_games,
    "npb_probable_pitchers":  games_to_probable(today_games),
    "npb_probable_tomorrow":  games_to_probable(tomorrow_games),
}

with open("npb_stats.json", "w", encoding="utf-8") as f:
    json.dump(output, f, separators=(",", ":"), ensure_ascii=False)

size_kb = len(json.dumps(output, ensure_ascii=False)) / 1024
print(f"\nOK npb_stats.json -- {size_kb:.1f} KB")
print(f"   batting:{len(npb_batting)} pitching:{len(npb_pitching)}")
print(f"   today:{len(today_games)} tomorrow:{len(tomorrow_games)}")
