"""
fetch_npb_stats.py
Genera npb_stats.json usando npb-scraper + npb.jp/bis/eng
Corre via GitHub Actions una vez al día.

Instalar: pip install npb-scraper pandas requests beautifulsoup4
"""

import json
import datetime
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import requests
from bs4 import BeautifulSoup

TODAY  = datetime.date.today()
SEASON = TODAY.year

print(f"[fetch_npb_stats] {TODAY}  season={SEASON}")

# ─── helper ──────────────────────────────────────────────────────────────────
def safe(val):
    try:
        if val is None: return None
        f = float(str(val).replace(',',''))
        import math
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 3)
    except (TypeError, ValueError):
        return str(val) if val else None

def df_to_records(df, cols):
    available = [c for c in cols if c in df.columns]
    missing   = [c for c in cols if c not in df.columns]
    if missing: print(f"  ⚠ columnas no encontradas: {missing}")
    out = []
    for _, row in df[available].iterrows():
        rec = {}
        for c in available:
            try:
                val = row[c]
                if pd.isna(val): rec[c] = None
                elif pd.api.types.is_numeric_dtype(df[c]): rec[c] = safe(val)
                else: rec[c] = str(val)
            except: rec[c] = None
        out.append(rec)
    return out

# ═══════════════════════════════════════════════════════════════════════════
# 1. NPB BATTING STATS (npb-scraper)
# ═══════════════════════════════════════════════════════════════════════════
print("→ npb batting (npb-scraper)...")
npb_batting = []
npb_pitching = []
npb_team_batting = []
npb_team_pitching = []

try:
    import npb_scraper as npb

    # Individual batting
    bat_df = npb.batting_stats(SEASON)
    bat_cols = ['Name','Team','G','AB','R','H','HR','RBI','BB','SO',
                'AVG','OBP','SLG','OPS','OPS+','BB%','K%','WAR']
    npb_batting = df_to_records(bat_df, bat_cols)
    print(f"   {len(npb_batting)} bateadores")

    # Individual pitching
    pit_df = npb.pitching_stats(SEASON)
    pit_cols = ['Name','Team','G','GS','IP','W','L','ERA','FIP','WHIP',
                'K/9','BB/9','K%','BB%','ERA+','BABIP','WAR']
    npb_pitching = df_to_records(pit_df, pit_cols)
    print(f"   {len(npb_pitching)} pitchers")

    # Team batting
    try:
        tbat_df = npb.team_batting(SEASON)
        tbat_cols = ['Team','G','AVG','OBP','SLG','OPS','OPS+','HR','R','BB','K','WAR']
        npb_team_batting = df_to_records(tbat_df, tbat_cols)
        print(f"   {len(npb_team_batting)} equipos batting")
    except Exception as e:
        print(f"   team batting error: {e}")

    # Team pitching
    try:
        tpit_df = npb.team_pitching(SEASON)
        tpit_cols = ['Team','G','ERA','FIP','WHIP','K/9','BB/9','ERA+','IP','WAR']
        npb_team_pitching = df_to_records(tpit_df, tpit_cols)
        print(f"   {len(npb_team_pitching)} equipos pitching")
    except Exception as e:
        print(f"   team pitching error: {e}")

except ImportError:
    print("   npb-scraper no instalado, usando scraping directo de npb.jp...")

    # ── Fallback: scrape npb.jp/bis/eng directly ──────────────────────────
    HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; NPBStatBot/1.0)'}

    # Team standings from npb.jp
    try:
        for league_id in ['cl', 'pl']:
            url = f'https://npb.jp/bis/eng/{SEASON}/standings/{league_id}standings.html'
            res = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cells = [c.get_text(strip=True) for c in row.find_all(['td','th'])]
                    if len(cells) >= 4 and cells[0]:
                        npb_team_batting.append({
                            'Team': cells[0], 'League': league_id.upper(),
                            'W': safe(cells[1]), 'L': safe(cells[2]),
                            'T': safe(cells[3]), 'PCT': safe(cells[4]) if len(cells)>4 else None
                        })
        print(f"   {len(npb_team_batting)} equipos (standings)")
    except Exception as e:
        print(f"   standings scraping error: {e}")

    # Individual stats from npb.jp/bis/eng
    try:
        # Batting leaders
        url = f'https://npb.jp/bis/eng/{SEASON}/stats/idp_b.html'
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if table:
            headers_row = [th.get_text(strip=True) for th in table.find_all('th')]
            for row in table.find_all('tr')[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= len(headers_row) and cells:
                    rec = {}
                    for i, h in enumerate(headers_row):
                        if i < len(cells): rec[h] = cells[i]
                    if rec.get('Name') or rec.get('Player'):
                        npb_batting.append(rec)
        print(f"   {len(npb_batting)} bateadores (npb.jp scrape)")
    except Exception as e:
        print(f"   batting scraping error: {e}")

    # Pitching leaders
    try:
        url = f'https://npb.jp/bis/eng/{SEASON}/stats/idp_p.html'
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if table:
            headers_row = [th.get_text(strip=True) for th in table.find_all('th')]
            for row in table.find_all('tr')[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 3 and cells:
                    rec = {}
                    for i, h in enumerate(headers_row):
                        if i < len(cells): rec[h] = cells[i]
                    if rec: npb_pitching.append(rec)
        print(f"   {len(npb_pitching)} pitchers (npb.jp scrape)")
    except Exception as e:
        print(f"   pitching scraping error: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# 2. PITCHER PROBABLE del día (npb.jp/announcement/starter)
# ═══════════════════════════════════════════════════════════════════════════
print("→ pitchers probables del día...")
probable_pitchers = {}
try:
    HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; NPBStatBot/1.0)'}
    url = f'https://npb.jp/bis/eng/{SEASON}/calendar/{TODAY.strftime("%Y%m%d")}.html'
    res = requests.get(url, headers=HEADERS, timeout=10)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 3:
                    home   = cells[0] if cells[0] else None
                    away   = cells[1] if len(cells)>1 else None
                    hpitch = cells[2] if len(cells)>2 else 'TBD'
                    apitch = cells[3] if len(cells)>3 else 'TBD'
                    if home: probable_pitchers[home] = {'pitcher': hpitch or 'TBD', 'isHome': True}
                    if away: probable_pitchers[away] = {'pitcher': apitch or 'TBD', 'isHome': False}
    print(f"   {len(probable_pitchers)} equipos con pitcher probable")
except Exception as e:
    print(f"   probable pitchers error: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# 3. ENSAMBLE FINAL
# ═══════════════════════════════════════════════════════════════════════════
output = {
    "generated_at":        TODAY.isoformat(),
    "season":              SEASON,
    "npb_batting":         npb_batting,
    "npb_pitching":        npb_pitching,
    "npb_team_batting":    npb_team_batting,
    "npb_team_pitching":   npb_team_pitching,
    "npb_probable_pitchers": probable_pitchers,
}

with open("npb_stats.json", "w") as f:
    json.dump(output, f, separators=(",", ":"))

size_kb = len(json.dumps(output)) / 1024
print(f"\n✅ npb_stats.json generado — {size_kb:.1f} KB")
print(f"   batting: {len(npb_batting)} | pitching: {len(npb_pitching)}")
print(f"   team_bat: {len(npb_team_batting)} | team_pit: {len(npb_team_pitching)}")
print(f"   probable_pitchers: {len(probable_pitchers)}")
