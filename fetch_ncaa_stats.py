"""
fetch_mlb_stats.py v3
- FanGraphs via API JSON directa (sin pybaseball scraper legacy)
- Statcast via pybaseball (solo pitch_mix y velo)
- Fixes: barrel column check, date comparison fix
"""

import json, warnings, datetime, math
warnings.filterwarnings("ignore")

import pandas as pd
import pybaseball
from pybaseball import statcast, pitching_stats_range, batting_stats_range
import requests

pybaseball.cache.enable()

SEASON = 2026
TODAY  = datetime.date.today()
START  = f"{SEASON}-03-20"
END    = TODAY.strftime("%Y-%m-%d")

print(f"[fetch_mlb_stats v3] {TODAY}  season={SEASON}")

def safe(val):
    try:
        if val is None: return None
        f = float(val)
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 3)
    except: return str(val) if val else None

def df_to_records(df, cols):
    available = [c for c in cols if c in df.columns]
    missing   = [c for c in cols if c not in df.columns]
    if missing: print(f"  ⚠ missing cols: {missing}")
    out = []
    for _, row in df[available].iterrows():
        rec = {}
        for c in available:
            v = row[c]
            try:
                rec[c] = safe(v) if pd.api.types.is_numeric_dtype(df[c]) else (str(v) if pd.notna(v) else None)
            except: rec[c] = None
        out.append(rec)
    return out

# ════ 1. FanGraphs via API JSON directa ════════════════════════════════
FG_BASE = "https://www.fangraphs.com/api/leaders/major-league/data"
FG_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.fangraphs.com/',
    'Accept': 'application/json',
}

def fg_fetch(stats_type, extra_params={}):
    params = {
        'age': '', 'pos': 'all', 'stats': stats_type,
        'lg': 'all', 'qual': '0', 'season': SEASON,
        'season1': SEASON, 'startdate': '', 'enddate': '',
        'month': '0', 'hand': '', 'team': '0',
        'pageitems': '5000', 'pagenum': '1',
        'ind': '0', 'rost': '0', 'players': '',
        'type': '8', 'postseason': '', 'sortdir': 'default',
        'sortstat': 'WAR',
    }
    params.update(extra_params)
    try:
        r = requests.get(FG_BASE, params=params, headers=FG_HEADERS, timeout=20)
        r.raise_for_status()
        data = r.json()
        records = data.get('data', [])
        print(f"  FG {stats_type}: {len(records)} records")
        return records
    except Exception as e:
        print(f"  FG ERROR {stats_type}: {e}")
        return []

# ── 1a. Batting (FanGraphs) ──────────────────────────────────────────────
print("→ batting_stats (FanGraphs API)...")
bat_raw = fg_fetch('bat')
batting = []
for r in bat_raw:
    rec = {
        'Name':     r.get('PlayerName') or r.get('Name',''),
        'Team':     r.get('Team',''),
        'G':        safe(r.get('G')),
        'AB':       safe(r.get('AB')),
        'PA':       safe(r.get('PA')),
        'H':        safe(r.get('H')),
        'HR':       safe(r.get('HR')),
        'RBI':      safe(r.get('RBI')),
        'BB':       safe(r.get('BB')),
        'SO':       safe(r.get('SO')),
        'AVG':      safe(r.get('AVG')),
        'OBP':      safe(r.get('OBP')),
        'SLG':      safe(r.get('SLG')),
        'OPS':      safe(r.get('OPS')),
        'wOBA':     safe(r.get('wOBA')),
        'wRC+':     safe(r.get('wRC+')),
        'BB%':      safe(r.get('BB%')),
        'K%':       safe(r.get('K%')),
        'ISO':      safe(r.get('ISO')),
        'BABIP':    safe(r.get('BABIP')),
        'Barrel%':  safe(r.get('Barrel%')),
        'HardHit%': safe(r.get('HardHit%')),
        'xBA':      safe(r.get('xBA')),
        'EV':       safe(r.get('EV')),
        'WAR':      safe(r.get('WAR')),
        'playerid': r.get('playerid') or r.get('xMLBAMID'),
    }
    if rec['Name']: batting.append(rec)
print(f"   {len(batting)} bateadores")

# ── 1b. Pitching (FanGraphs) ─────────────────────────────────────────────
print("→ pitching_stats (FanGraphs API)...")
pit_raw = fg_fetch('pit')
pitching = []
for r in pit_raw:
    rec = {
        'Name':     r.get('PlayerName') or r.get('Name',''),
        'Team':     r.get('Team',''),
        'G':        safe(r.get('G')),
        'GS':       safe(r.get('GS')),
        'IP':       safe(r.get('IP')),
        'W':        safe(r.get('W')),
        'L':        safe(r.get('L')),
        'SV':       safe(r.get('SV')),
        'ERA':      safe(r.get('ERA')),
        'FIP':      safe(r.get('FIP')),
        'xFIP':     safe(r.get('xFIP')),
        'WHIP':     safe(r.get('WHIP')),
        'K/9':      safe(r.get('K/9')),
        'BB/9':     safe(r.get('BB/9')),
        'HR/9':     safe(r.get('HR/9')),
        'K%':       safe(r.get('K%')),
        'BB%':      safe(r.get('BB%')),
        'BABIP':    safe(r.get('BABIP')),
        'LOB%':     safe(r.get('LOB%')),
        'GB%':      safe(r.get('GB%')),
        'FB%':      safe(r.get('FB%')),
        'Hard%':    safe(r.get('Hard%')),
        'Barrel%':  safe(r.get('Barrel%')),
        'F-Strike%':safe(r.get('F-Strike%')),
        'FBv':      safe(r.get('FBv')),
        'QS':       safe(r.get('QS')),
        'WAR':      safe(r.get('WAR')),
        'playerid': r.get('playerid') or r.get('xMLBAMID'),
    }
    if rec['Name']: pitching.append(rec)
print(f"   {len(pitching)} pitchers")

# ── 1c. Team batting & pitching ───────────────────────────────────────────
print("→ team stats (FanGraphs API)...")
team_bat_raw = fg_fetch('bat', {'team': '0', 'players': '0', 'type': '8'})
# FanGraphs team endpoint
try:
    r = requests.get("https://www.fangraphs.com/api/leaders/major-league/data",
        params={'stats':'bat','lg':'all','qual':'0','season':SEASON,'season1':SEASON,
                'type':'8','team':'0,ts','pageitems':'50'},
        headers=FG_HEADERS, timeout=15)
    team_bat = []
    if r.ok:
        for t in r.json().get('data',[]):
            team_bat.append({
                'Team': t.get('Team',''), 'AVG': safe(t.get('AVG')),
                'OBP': safe(t.get('OBP')), 'SLG': safe(t.get('SLG')),
                'OPS': safe(t.get('OPS')), 'wOBA': safe(t.get('wOBA')),
                'wRC+': safe(t.get('wRC+')), 'WAR': safe(t.get('WAR')),
            })
    print(f"   team_bat: {len(team_bat)}")
except Exception as e:
    print(f"   team_bat error: {e}"); team_bat = []

try:
    r = requests.get("https://www.fangraphs.com/api/leaders/major-league/data",
        params={'stats':'pit','lg':'all','qual':'0','season':SEASON,'season1':SEASON,
                'type':'8','team':'0,ts','pageitems':'50'},
        headers=FG_HEADERS, timeout=15)
    team_pit = []
    if r.ok:
        for t in r.json().get('data',[]):
            team_pit.append({
                'Team': t.get('Team',''), 'ERA': safe(t.get('ERA')),
                'FIP': safe(t.get('FIP')), 'xFIP': safe(t.get('xFIP')),
                'WHIP': safe(t.get('WHIP')), 'K/9': safe(t.get('K/9')),
                'BB/9': safe(t.get('BB/9')), 'WAR': safe(t.get('WAR')),
            })
    print(f"   team_pit: {len(team_pit)}")
except Exception as e:
    print(f"   team_pit error: {e}"); team_pit = []

# ════ 2. STATCAST últimos 7d ════════════════════════════════════════════
print("→ statcast (últimos 7 días)...")
start_7d = (TODAY - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
pitch_mix = {}
statcast_batters = []

try:
    sc_df = statcast(start_dt=start_7d, end_dt=END)
    print(f"   {len(sc_df)} pitches raw")
    print(f"   columns: {list(sc_df.columns[:20])}")

    # ── Pitch mix por pitcher ────────────────────────────────────────────
    needed_cols = ['pitcher','player_name','pitch_type','release_speed','release_spin_rate']
    avail = [c for c in needed_cols if c in sc_df.columns]
    sc_sub = sc_df[avail].dropna(subset=['pitcher'])

    for pid, grp in sc_sub.groupby('pitcher'):
        name = grp['player_name'].iloc[0] if 'player_name' in grp.columns else '—'
        mix = {}
        total = len(grp)
        if 'pitch_type' in grp.columns:
            for pt, cnt in grp['pitch_type'].value_counts().items():
                sub = grp[grp['pitch_type'] == pt]
                mix[str(pt)] = {
                    'pct': round(cnt/total*100, 1),
                    'avg_velo': safe(sub['release_speed'].mean()) if 'release_speed' in sub.columns else None,
                    'avg_spin': safe(sub['release_spin_rate'].mean()) if 'release_spin_rate' in sub.columns else None,
                }
        pitch_mix[int(pid)] = {'name': str(name), 'mix': mix}
    print(f"   pitch_mix: {len(pitch_mix)} pitchers")

    # ── Statcast batter aggregates ───────────────────────────────────────
    bat_cols_needed = ['batter','player_name','stand','estimated_ba_using_speedangle',
                       'launch_speed','p_throws']
    bat_avail = [c for c in bat_cols_needed if c in sc_df.columns]
    sc_bat = sc_df[bat_avail].dropna(subset=['batter'])

    for bid, grp in sc_bat.groupby('batter'):
        name = grp['player_name'].iloc[0] if 'player_name' in grp.columns else '—'
        n = len(grp)
        rec = {'batter_id': int(bid), 'name': str(name), 'pitches_seen': n}

        if 'stand' in grp.columns:
            rec['bat_side'] = grp['stand'].mode()[0] if len(grp) > 0 else None

        if 'estimated_ba_using_speedangle' in grp.columns:
            xba = grp['estimated_ba_using_speedangle']
            rec['xBA'] = safe(xba.mean())
            if 'p_throws' in grp.columns:
                rec['xBA_vsL'] = safe(grp[grp['p_throws']=='L']['estimated_ba_using_speedangle'].mean()) if len(grp[grp['p_throws']=='L'])>=5 else None
                rec['xBA_vsR'] = safe(grp[grp['p_throws']=='R']['estimated_ba_using_speedangle'].mean()) if len(grp[grp['p_throws']=='R'])>=5 else None

        if 'launch_speed' in grp.columns:
            ls = grp['launch_speed'].dropna()
            rec['avg_exit_vel'] = safe(ls.mean())
            rec['hard_hit_pct'] = safe(len(ls[ls>=95])/n*100) if n > 0 else None
            # barrel — check column exists
            if 'barrel' in grp.columns:
                rec['barrel_pct'] = safe(grp['barrel'].sum()/n*100)

        statcast_batters.append(rec)
    print(f"   statcast_batters: {len(statcast_batters)}")

except Exception as e:
    print(f"   ERROR statcast: {e}")

# ════ 3. VELO DELTA 30d ═════════════════════════════════════════════════
print("→ statcast velo 30d...")
start_30d = (TODAY - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
try:
    sc_30d = statcast(start_dt=start_30d, end_dt=END)
    needed = ['pitcher','player_name','release_speed','pitch_type','game_date']
    avail  = [c for c in needed if c in sc_30d.columns]
    sc_velo = sc_30d[avail].dropna(subset=['pitcher','release_speed'])

    # Fix date type
    if 'game_date' in sc_velo.columns:
        sc_velo = sc_velo.copy()
        sc_velo['game_date'] = pd.to_datetime(sc_velo['game_date'], errors='coerce')

    cutoff_7d = pd.Timestamp(TODAY) - pd.Timedelta(days=7)

    for pid, grp in sc_velo.groupby('pitcher'):
        pid_int = int(pid)
        name = grp['player_name'].iloc[0] if 'player_name' in grp.columns else '—'

        fb_types = ['FF','SI','FC']
        fb_grp = grp[grp['pitch_type'].isin(fb_types)] if 'pitch_type' in grp.columns else grp

        avg_velo_30d = safe(fb_grp['release_speed'].mean()) if len(fb_grp)>=10 else None

        recent_7d = fb_grp[fb_grp['game_date'] >= cutoff_7d] if 'game_date' in fb_grp.columns else pd.DataFrame()
        avg_velo_recent = safe(recent_7d['release_speed'].mean()) if len(recent_7d)>=5 else avg_velo_30d
        velo_delta = round(avg_velo_recent - avg_velo_30d, 2) if (avg_velo_recent and avg_velo_30d) else None

        if pid_int in pitch_mix:
            pitch_mix[pid_int].update({
                'avg_velo_30d': avg_velo_30d,
                'avg_velo_recent': avg_velo_recent,
                'velo_delta': velo_delta,
            })
    print(f"   velo_delta: {len(pitch_mix)} pitchers")
except Exception as e:
    print(f"   ERROR velo 30d: {e}")

# ════ 4. RECENT 14d (pybaseball range) ═════════════════════════════════
print("→ batting/pitching recent 14d...")
start_14d = (TODAY - datetime.timedelta(days=14)).strftime("%Y-%m-%d")
batting_recent = []
pitching_recent = []

try:
    bat_r = batting_stats_range(start_14d, END)
    if bat_r is not None and len(bat_r):
        batting_recent = df_to_records(bat_r, [
            'Name','Team','G','AB','PA','H','HR','RBI','BB','SO',
            'AVG','OBP','SLG','OPS','wOBA','wRC+','ISO','BABIP'
        ])
    print(f"   batting_recent: {len(batting_recent)}")
except Exception as e:
    print(f"   batting_recent error: {e}")

try:
    pit_r = pitching_stats_range(start_14d, END)
    if pit_r is not None and len(pit_r):
        pitching_recent = df_to_records(pit_r, [
            'Name','Team','G','GS','IP','W','L',
            'ERA','FIP','WHIP','K/9','BB/9','K%','BB%','LOB%','GB%'
        ])
    print(f"   pitching_recent: {len(pitching_recent)}")
except Exception as e:
    print(f"   pitching_recent error: {e}")

# ════ 5. OUTPUT ══════════════════════════════════════════════════════════
output = {
    "generated_at":     TODAY.isoformat(),
    "season":           SEASON,
    "statcast_window":  f"{start_7d} → {END}",
    "recent_window":    f"{start_14d} → {END}",
    "batting":          batting,
    "pitching":         pitching,
    "batting_recent":   batting_recent,
    "pitching_recent":  pitching_recent,
    "statcast_batters": statcast_batters,
    "pitch_mix":        pitch_mix,
    "team_batting":     team_bat,
    "team_pitching":    team_pit,
}

with open("mlb_stats.json", "w") as f:
    json.dump(output, f, separators=(",",":"))

size_kb = len(json.dumps(output)) / 1024
print(f"\n✅ mlb_stats.json v3 — {size_kb:.1f} KB")
print(f"   batting:{len(batting)} | pitching:{len(pitching)}")
print(f"   batting_recent:{len(batting_recent)} | pitching_recent:{len(pitching_recent)}")
print(f"   statcast_batters:{len(statcast_batters)} | pitch_mix:{len(pitch_mix)}")
print(f"   team_bat:{len(team_bat)} | team_pit:{len(team_pit)}")
