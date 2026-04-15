"""
fetch_ncaa_stats.py
Genera ncaa_stats.json usando collegebaseball (stats.ncaa.org)
Corre via GitHub Actions una vez al día.
pip install git+https://github.com/nathanblumenfeld/collegebaseball
"""

import json, datetime, warnings
warnings.filterwarnings("ignore")
import pandas as pd

TODAY  = datetime.date.today()
SEASON = TODAY.year
print(f"[fetch_ncaa_stats] {TODAY} season={SEASON}")

def safe(val):
    try:
        if val is None or str(val).strip() in ('','-','nan'): return None
        return round(float(str(val).replace(',','')), 3)
    except: return str(val).strip() if val else None

def df_records(df, cols):
    avail = [c for c in cols if c in df.columns]
    miss  = [c for c in cols if c not in df.columns]
    if miss: print(f"  ⚠ missing: {miss}")
    out = []
    for _, row in df[avail].iterrows():
        rec = {}
        for c in avail:
            try:
                v = row[c]
                rec[c] = safe(v) if pd.api.types.is_numeric_dtype(df[c]) else (str(v) if pd.notna(v) else None)
            except: rec[c] = None
        out.append(rec)
    return out

ncaa_pitching   = []
ncaa_batting    = []
ncaa_team_stats = []

try:
    from collegebaseball import ncaa_scraper

    # ── Individual pitching ──────────────────────────────────────
    print("→ NCAA pitching...")
    try:
        pit_df = ncaa_scraper.get_pitching_stats(year=SEASON, division=1)
        # Rename columns to standard names
        col_map = {
            'Player':'name','Team':'team','ERA':'era','WHIP':'whip',
            'IP':'ip','W':'w','L':'l','SO':'k','BB':'bb',
            'H':'h','HR':'hr','R':'r','ER':'er',
            'App':'g','GS':'gs'
        }
        pit_df = pit_df.rename(columns={k:v for k,v in col_map.items() if k in pit_df.columns})
        # Compute K/9 and BB/9
        if 'ip' in pit_df.columns and 'k' in pit_df.columns:
            pit_df['ip_f'] = pd.to_numeric(pit_df['ip'], errors='coerce')
            pit_df['k_f']  = pd.to_numeric(pit_df['k'],  errors='coerce')
            pit_df['bb_f'] = pd.to_numeric(pit_df.get('bb', 0), errors='coerce').fillna(0)
            pit_df['k9']   = (pit_df['k_f'] / pit_df['ip_f'].replace(0, float('nan')) * 9).round(2)
            pit_df['bb9']  = (pit_df['bb_f'] / pit_df['ip_f'].replace(0, float('nan')) * 9).round(2)
        pit_cols = ['name','team','g','gs','ip','w','l','era','whip','k9','bb9','k','bb','hr']
        ncaa_pitching = df_records(pit_df, pit_cols)
        print(f"   {len(ncaa_pitching)} pitchers")
    except Exception as e:
        print(f"   pitching error: {e}")

    # ── Individual batting ───────────────────────────────────────
    print("→ NCAA batting...")
    try:
        bat_df = ncaa_scraper.get_batting_stats(year=SEASON, division=1)
        col_map = {
            'Player':'name','Team':'team','BA':'avg','OBPct':'obp','SlgPct':'slg',
            'AB':'ab','H':'h','HR':'hr','RBI':'rbi','BB':'bb','SO':'k',
            'R':'r','SB':'sb','GP':'g'
        }
        bat_df = bat_df.rename(columns={k:v for k,v in col_map.items() if k in bat_df.columns})
        if 'obp' in bat_df.columns and 'slg' in bat_df.columns:
            bat_df['ops'] = (pd.to_numeric(bat_df['obp'],errors='coerce') +
                             pd.to_numeric(bat_df['slg'],errors='coerce')).round(3)
        bat_cols = ['name','team','g','ab','avg','obp','slg','ops','hr','rbi','bb','k','r','sb']
        ncaa_batting = df_records(bat_df, bat_cols)
        print(f"   {len(ncaa_batting)} bateadores")
    except Exception as e:
        print(f"   batting error: {e}")

    # ── Team stats ────────────────────────────────────────────────
    print("→ NCAA team stats...")
    try:
        team_bat = ncaa_scraper.get_batting_stats(year=SEASON, division=1, team=True)
        team_pit = ncaa_scraper.get_pitching_stats(year=SEASON, division=1, team=True)
        # Merge on team name
        if not team_bat.empty and not team_pit.empty:
            tb = team_bat.rename(columns={'Team':'team','BA':'avg','OBPct':'obp','SlgPct':'slg'})
            tp = team_pit.rename(columns={'Team':'team','ERA':'era','WHIP':'whip'})
            merged = pd.merge(tb[['team','avg','obp','slg']],
                              tp[['team','era','whip']], on='team', how='outer')
            if 'obp' in merged.columns and 'slg' in merged.columns:
                merged['ops'] = (pd.to_numeric(merged['obp'],errors='coerce') +
                                 pd.to_numeric(merged['slg'],errors='coerce')).round(3)
            ncaa_team_stats = df_records(merged, ['team','avg','obp','slg','ops','era','whip'])
            print(f"   {len(ncaa_team_stats)} equipos")
    except Exception as e:
        print(f"   team stats error: {e}")

except ImportError:
    print("  collegebaseball not installed — using fallback scraping from stats.ncaa.org")
    import requests
    from bs4 import BeautifulSoup
    import time

    HEADERS = {'User-Agent': 'Mozilla/5.0'}
    # NCAA stats.ncaa.org fallback
    try:
        url = f"https://stats.ncaa.org/rankings/national_ranking?academic_year={SEASON}.0&division=1.0&ranking_period=1.0&sport_code=MBA&stat_seq=125.0"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table', id='rankings_table')
        if table:
            rows = table.find_all('tr')
            headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]
            for row in rows[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 3:
                    rec = {headers[i]: cells[i] for i in range(min(len(headers),len(cells)))}
                    ncaa_team_stats.append(rec)
        print(f"   fallback: {len(ncaa_team_stats)} teams")
    except Exception as e:
        print(f"   fallback error: {e}")

# ── Output ────────────────────────────────────────────────────────
output = {
    "generated_at":    TODAY.isoformat(),
    "season":          SEASON,
    "pitching":        ncaa_pitching,
    "batting":         ncaa_batting,
    "team_stats":      ncaa_team_stats,
}

with open("ncaa_stats.json", "w", encoding="utf-8") as f:
    json.dump(output, f, separators=(",",":"))

size_kb = len(json.dumps(output)) / 1024
print(f"\n✅ ncaa_stats.json — {size_kb:.1f} KB")
print(f"   pitching:{len(ncaa_pitching)} batting:{len(ncaa_batting)} teams:{len(ncaa_team_stats)}")
