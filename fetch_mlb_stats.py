"""
fetch_mlb_stats.py v4
- FanGraphs via API JSON directa
- MLB-StatsAPI: league_leaders, standings, run_differential, first5_innings
- Statcast: pitch_mix, velo_delta, batter aggregates
- pitcher_wl lookup desde MLB leaders (W-L real y actualizado)
"""

import json, warnings, datetime, math, time
warnings.filterwarnings("ignore")

import pandas as pd
import pybaseball
from pybaseball import statcast, pitching_stats_range, batting_stats_range
import requests

pybaseball.cache.enable()

SEASON  = 2026
TODAY   = datetime.date.today()
END     = TODAY.strftime("%Y-%m-%d")
MLBAPI  = "https://statsapi.mlb.com/api/v1"

print(f"[fetch_mlb_stats v4] {TODAY}  season={SEASON}")

def safe(val):
    try:
        if val is None: return None
        f = float(val)
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 3)
    except: return str(val) if val else None

def df_to_records(df, cols):
    available = [c for c in cols if c in df.columns]
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

def mlb_get(endpoint, params={}):
    try:
        r = requests.get(f"{MLBAPI}/{endpoint}", params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  MLB WARN /{endpoint}: {e}")
        return None

# ════════════════════════════════════════════════════════
# 1. FanGraphs API directa
# ════════════════════════════════════════════════════════
FG_BASE = "https://www.fangraphs.com/api/leaders/major-league/data"
FG_HDRS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.fangraphs.com/',
    'Accept': 'application/json',
}

def fg_fetch(stats_type, extra={}):
    params = {'age':'','pos':'all','stats':stats_type,'lg':'all','qual':'0',
              'season':SEASON,'season1':SEASON,'startdate':'','enddate':'',
              'month':'0','hand':'','team':'0','pageitems':'5000','pagenum':'1',
              'ind':'0','rost':'0','players':'','type':'8','postseason':'',
              'sortdir':'default','sortstat':'WAR'}
    params.update(extra)
    try:
        r = requests.get(FG_BASE, params=params, headers=FG_HDRS, timeout=20)
        r.raise_for_status()
        recs = r.json().get('data', [])
        print(f"  FG {stats_type}: {len(recs)}")
        return recs
    except Exception as e:
        print(f"  FG ERROR {stats_type}: {e}"); return []

print("→ batting (FanGraphs)...")
batting = []
for r in fg_fetch('bat'):
    rec = {'Name':r.get('PlayerName') or r.get('Name',''),'Team':r.get('Team',''),
           'G':safe(r.get('G')),'AB':safe(r.get('AB')),'PA':safe(r.get('PA')),
           'H':safe(r.get('H')),'HR':safe(r.get('HR')),'RBI':safe(r.get('RBI')),
           'BB':safe(r.get('BB')),'SO':safe(r.get('SO')),'AVG':safe(r.get('AVG')),
           'OBP':safe(r.get('OBP')),'SLG':safe(r.get('SLG')),'OPS':safe(r.get('OPS')),
           'wOBA':safe(r.get('wOBA')),'wRC+':safe(r.get('wRC+')),'BB%':safe(r.get('BB%')),
           'K%':safe(r.get('K%')),'ISO':safe(r.get('ISO')),'BABIP':safe(r.get('BABIP')),
           'Barrel%':safe(r.get('Barrel%')),'HardHit%':safe(r.get('HardHit%')),
           'xBA':safe(r.get('xBA')),'EV':safe(r.get('EV')),'WAR':safe(r.get('WAR')),
           'playerid':r.get('playerid') or r.get('xMLBAMID')}
    if rec['Name']: batting.append(rec)
print(f"   {len(batting)} bateadores")

print("→ pitching (FanGraphs)...")
pitching = []
for r in fg_fetch('pit'):
    rec = {'Name':r.get('PlayerName') or r.get('Name',''),'Team':r.get('Team',''),
           'G':safe(r.get('G')),'GS':safe(r.get('GS')),'IP':safe(r.get('IP')),
           'W':safe(r.get('W')),'L':safe(r.get('L')),'SV':safe(r.get('SV')),
           'ERA':safe(r.get('ERA')),'FIP':safe(r.get('FIP')),'xFIP':safe(r.get('xFIP')),
           'WHIP':safe(r.get('WHIP')),'K/9':safe(r.get('K/9')),'BB/9':safe(r.get('BB/9')),
           'HR/9':safe(r.get('HR/9')),'K%':safe(r.get('K%')),'BB%':safe(r.get('BB%')),
           'BABIP':safe(r.get('BABIP')),'LOB%':safe(r.get('LOB%')),'GB%':safe(r.get('GB%')),
           'FB%':safe(r.get('FB%')),'Hard%':safe(r.get('Hard%')),
           'F-Strike%':safe(r.get('F-Strike%')),'FBv':safe(r.get('FBv')),
           'QS':safe(r.get('QS')),'WAR':safe(r.get('WAR')),
           'playerid':r.get('playerid') or r.get('xMLBAMID')}
    if rec['Name']: pitching.append(rec)
print(f"   {len(pitching)} pitchers")

print("→ team stats (FanGraphs)...")
team_bat, team_pit = [], []
try:
    r = requests.get(FG_BASE, params={'stats':'bat','lg':'all','qual':'0','season':SEASON,
        'season1':SEASON,'type':'8','team':'0,ts','pageitems':'50'}, headers=FG_HDRS, timeout=15)
    if r.ok:
        for t in r.json().get('data',[]):
            team_bat.append({'Team':t.get('Team',''),'AVG':safe(t.get('AVG')),
                'OBP':safe(t.get('OBP')),'SLG':safe(t.get('SLG')),'OPS':safe(t.get('OPS')),
                'wOBA':safe(t.get('wOBA')),'wRC+':safe(t.get('wRC+')),'WAR':safe(t.get('WAR'))})
    print(f"   team_bat: {len(team_bat)}")
except Exception as e: print(f"   team_bat: {e}")

try:
    r = requests.get(FG_BASE, params={'stats':'pit','lg':'all','qual':'0','season':SEASON,
        'season1':SEASON,'type':'8','team':'0,ts','pageitems':'50'}, headers=FG_HDRS, timeout=15)
    if r.ok:
        for t in r.json().get('data',[]):
            team_pit.append({'Team':t.get('Team',''),'ERA':safe(t.get('ERA')),
                'FIP':safe(t.get('FIP')),'xFIP':safe(t.get('xFIP')),'WHIP':safe(t.get('WHIP')),
                'K/9':safe(t.get('K/9')),'BB/9':safe(t.get('BB/9')),'WAR':safe(t.get('WAR'))})
    print(f"   team_pit: {len(team_pit)}")
except Exception as e: print(f"   team_pit: {e}")

# ════════════════════════════════════════════════════════
# 2. MLB-StatsAPI League Leaders — W-L real del pitcher
# ════════════════════════════════════════════════════════
print("→ MLB league leaders (statsapi)...")
mlb_leaders = {}
LEADER_CATS = [
    ('earnedRunAverage','ERA'),('walksAndHitsPerInningPitched','WHIP'),
    ('strikeoutsPer9Inn','K9'),('wins','W'),('losses','L'),
    ('batterAverage','AVG'),('onBasePlusSlugging','OPS'),
    ('homeRuns','HR'),('runsBattedIn','RBI'),
]
for stat_name, label in LEADER_CATS:
    try:
        data = mlb_get('stats/leaders', {'leaderCategories':stat_name,'season':SEASON,'sportId':1,'limit':200})
        leaders = []
        for lg in (data.get('leagueLeaders') or []):
            for row in (lg.get('leaders') or []):
                p = row.get('person',{})
                leaders.append({'id':p.get('id'),'name':p.get('fullName',''),
                    'team':(row.get('team') or {}).get('name',''),
                    'value':safe(row.get('value')),'rank':row.get('rank')})
        mlb_leaders[label] = leaders
        print(f"   {label}: {len(leaders)}")
        time.sleep(0.3)
    except Exception as e:
        print(f"   leaders {label}: {e}"); mlb_leaders[label] = []

# Build W-L lookup and merge into pitching
pitcher_wl = {}
for row in mlb_leaders.get('W',[]): 
    if row['id']: pitcher_wl.setdefault(row['id'],{'name':row['name'],'team':row['team'],'w':0,'l':0})['w']=int(row['value'] or 0)
for row in mlb_leaders.get('L',[]): 
    if row['id']: pitcher_wl.setdefault(row['id'],{'name':row['name'],'team':row['team'],'w':0,'l':0})['l']=int(row['value'] or 0)
wl_by_name = {v['name'].lower():v for v in pitcher_wl.values()}
for p in pitching:
    nk = p.get('Name','').lower()
    if nk in wl_by_name:
        if p.get('W') is None: p['W'] = wl_by_name[nk]['w']
        if p.get('L') is None: p['L'] = wl_by_name[nk]['l']
print(f"   pitcher_wl: {len(pitcher_wl)}")

# ════════════════════════════════════════════════════════
# 3. Standings + Run Differential
# ════════════════════════════════════════════════════════
print("→ standings + run differential...")
standings = []
try:
    for lg_id in [103, 104]:
        data = mlb_get('standings', {'leagueId':lg_id,'season':SEASON,
            'standingsTypes':'regularSeason','hydrate':'team,division'})
        for record in (data.get('records') or []):
            div = (record.get('division') or {}).get('name','')
            for tr in (record.get('teamRecords') or []):
                team = (tr.get('team') or {}).get('name','')
                rs = safe(tr.get('runsScored'))
                ra = safe(tr.get('runsAllowed'))
                # Parse split records for home/away/last10
                splits = {}
                for sp in (tr.get('records',{}).get('splitRecords') or []):
                    splits[sp.get('type','')] = sp
                standings.append({
                    'team':team,'division':div,
                    'w':tr.get('wins',0),'l':tr.get('losses',0),
                    'pct':safe(tr.get('winningPercentage')),
                    'gb':tr.get('gamesBack','—'),
                    'runs_scored':rs,'runs_allowed':ra,
                    'run_diff':round(rs-ra,0) if (rs and ra) else None,
                    'home_w':splits.get('home',{}).get('wins',0),
                    'home_l':splits.get('home',{}).get('losses',0),
                    'away_w':splits.get('away',{}).get('wins',0),
                    'away_l':splits.get('away',{}).get('losses',0),
                    'last10_w':splits.get('lastTen',{}).get('wins',0),
                    'last10_l':splits.get('lastTen',{}).get('losses',0),
                    'streak':(tr.get('streak') or {}).get('streakCode',''),
                })
        time.sleep(0.3)
    print(f"   standings: {len(standings)}")
except Exception as e: print(f"   standings error: {e}")

# ════════════════════════════════════════════════════════
# 4. First 5 Innings — scoring by inning (last 7 days)
# ════════════════════════════════════════════════════════
print("→ first 5 innings data (last 7 days)...")
first5_by_team = {}
first5_stats = []
try:
    sched = mlb_get('schedule', {'sportId':1,
        'startDate':(TODAY-datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
        'endDate':END,'hydrate':'linescore','gameType':'R'})
    games_done = 0
    for de in (sched.get('dates') or []):
        for game in (de.get('games') or []):
            if game.get('status',{}).get('codedGameState') != 'F': continue
            innings = game.get('linescore',{}).get('innings',[])
            if not innings: continue
            ht = (game.get('teams',{}).get('home',{}).get('team',{}) or {}).get('name','')
            at = (game.get('teams',{}).get('away',{}).get('team',{}) or {}).get('name','')
            he = sum(int(i.get('home',{}).get('runs',0) or 0) for i in innings[:5])
            ae = sum(int(i.get('away',{}).get('runs',0) or 0) for i in innings[:5])
            for tname, scored, allowed in [(ht,he,ae),(at,ae,he)]:
                if not tname: continue
                d = first5_by_team.setdefault(tname,{'scored':0,'allowed':0,'games':0})
                d['scored']+=scored; d['allowed']+=allowed; d['games']+=1
            games_done+=1
    for team, d in first5_by_team.items():
        g = max(d['games'],1)
        first5_stats.append({'team':team,'games':d['games'],
            'avg_scored_f5':round(d['scored']/g,2),
            'avg_allowed_f5':round(d['allowed']/g,2),
            'run_diff_f5':round((d['scored']-d['allowed'])/g,2)})
    first5_stats.sort(key=lambda x:x['run_diff_f5'],reverse=True)
    print(f"   first5: {len(first5_stats)} teams from {games_done} games")
except Exception as e: print(f"   first5 error: {e}")

# ════════════════════════════════════════════════════════
# 5. Statcast 7d + velo 30d
# ════════════════════════════════════════════════════════
print("→ statcast (7 días)...")
start_7d  = (TODAY-datetime.timedelta(days=7)).strftime("%Y-%m-%d")
start_30d = (TODAY-datetime.timedelta(days=30)).strftime("%Y-%m-%d")
pitch_mix = {}; statcast_batters = []

try:
    sc = statcast(start_dt=start_7d, end_dt=END)
    print(f"   {len(sc)} pitches")
    needed = ['pitcher','player_name','pitch_type','release_speed','release_spin_rate']
    sc_sub = sc[[c for c in needed if c in sc.columns]].dropna(subset=['pitcher'])
    for pid, grp in sc_sub.groupby('pitcher'):
        name = grp['player_name'].iloc[0] if 'player_name' in grp.columns else '—'
        mix={}; total=len(grp)
        if 'pitch_type' in grp.columns:
            for pt,cnt in grp['pitch_type'].value_counts().items():
                sub=grp[grp['pitch_type']==pt]
                mix[str(pt)]={'pct':round(cnt/total*100,1),
                    'avg_velo':safe(sub['release_speed'].mean()) if 'release_speed' in sub.columns else None,
                    'avg_spin':safe(sub['release_spin_rate'].mean()) if 'release_spin_rate' in sub.columns else None}
        pitch_mix[int(pid)]={'name':str(name),'mix':mix}
    print(f"   pitch_mix: {len(pitch_mix)}")

    bat_cols=['batter','player_name','stand','estimated_ba_using_speedangle','launch_speed','p_throws']
    sc_bat=sc[[c for c in bat_cols if c in sc.columns]].dropna(subset=['batter'])
    for bid,grp in sc_bat.groupby('batter'):
        name=grp['player_name'].iloc[0] if 'player_name' in grp.columns else '—'
        n=len(grp); rec={'batter_id':int(bid),'name':str(name),'pitches_seen':n}
        if 'stand' in grp.columns: rec['bat_side']=grp['stand'].mode()[0]
        if 'estimated_ba_using_speedangle' in grp.columns:
            rec['xBA']=safe(grp['estimated_ba_using_speedangle'].mean())
            if 'p_throws' in grp.columns:
                rec['xBA_vsL']=safe(grp[grp['p_throws']=='L']['estimated_ba_using_speedangle'].mean()) if len(grp[grp['p_throws']=='L'])>=5 else None
                rec['xBA_vsR']=safe(grp[grp['p_throws']=='R']['estimated_ba_using_speedangle'].mean()) if len(grp[grp['p_throws']=='R'])>=5 else None
        if 'launch_speed' in grp.columns:
            ls=grp['launch_speed'].dropna()
            rec['avg_exit_vel']=safe(ls.mean()); rec['hard_hit_pct']=safe(len(ls[ls>=95])/n*100) if n>0 else None
            if 'barrel' in grp.columns: rec['barrel_pct']=safe(grp['barrel'].sum()/n*100)
        statcast_batters.append(rec)
    print(f"   statcast_batters: {len(statcast_batters)}")
except Exception as e: print(f"   statcast error: {e}")

print("→ velo 30d...")
try:
    sc30=statcast(start_dt=start_30d,end_dt=END)
    needed=['pitcher','player_name','release_speed','pitch_type','game_date']
    sv=sc30[[c for c in needed if c in sc30.columns]].dropna(subset=['pitcher','release_speed']).copy()
    if 'game_date' in sv.columns: sv['game_date']=pd.to_datetime(sv['game_date'],errors='coerce')
    cut=pd.Timestamp(TODAY)-pd.Timedelta(days=7)
    for pid,grp in sv.groupby('pitcher'):
        pid_int=int(pid)
        fb=grp[grp['pitch_type'].isin(['FF','SI','FC'])] if 'pitch_type' in grp.columns else grp
        a30=safe(fb['release_speed'].mean()) if len(fb)>=10 else None
        r7=fb[fb['game_date']>=cut] if 'game_date' in fb.columns else pd.DataFrame()
        a7=safe(r7['release_speed'].mean()) if len(r7)>=5 else a30
        delta=round(a7-a30,2) if (a7 and a30) else None
        if pid_int in pitch_mix: pitch_mix[pid_int].update({'avg_velo_30d':a30,'avg_velo_recent':a7,'velo_delta':delta})
    print(f"   velo_delta done")
except Exception as e: print(f"   velo 30d: {e}")

# ════════════════════════════════════════════════════════
# 6. Recent 14d
# ════════════════════════════════════════════════════════
print("→ recent 14d...")
start_14d=(TODAY-datetime.timedelta(days=14)).strftime("%Y-%m-%d")
batting_recent,pitching_recent=[],[]
try:
    br=batting_stats_range(start_14d,END)
    if br is not None and len(br):
        batting_recent=df_to_records(br,['Name','Team','G','AB','PA','H','HR','RBI','BB','SO','AVG','OBP','SLG','OPS','wOBA','wRC+','ISO','BABIP'])
    print(f"   batting_recent: {len(batting_recent)}")
except Exception as e: print(f"   batting_recent: {e}")
try:
    pr=pitching_stats_range(start_14d,END)
    if pr is not None and len(pr):
        pitching_recent=df_to_records(pr,['Name','Team','G','GS','IP','W','L','ERA','FIP','WHIP','K/9','BB/9','K%','BB%','LOB%','GB%'])
    print(f"   pitching_recent: {len(pitching_recent)}")
except Exception as e: print(f"   pitching_recent: {e}")

# ════════════════════════════════════════════════════════
# 7. Output
# ════════════════════════════════════════════════════════
output = {
    "generated_at":TODAY.isoformat(),"season":SEASON,
    "statcast_window":f"{start_7d} → {END}","recent_window":f"{start_14d} → {END}",
    "batting":batting,"pitching":pitching,
    "batting_recent":batting_recent,"pitching_recent":pitching_recent,
    "statcast_batters":statcast_batters,"pitch_mix":pitch_mix,
    "team_batting":team_bat,"team_pitching":team_pit,
    "standings":standings,"first5_stats":first5_stats,
    "mlb_leaders":mlb_leaders,"pitcher_wl":{str(k):v for k,v in pitcher_wl.items()},
}

with open("mlb_stats.json","w") as f:
    json.dump(output,f,separators=(",",":"))

size_kb=len(json.dumps(output))/1024
print(f"\n✅ mlb_stats.json v4 — {size_kb:.1f} KB")
print(f"   batting:{len(batting)} pitching:{len(pitching)}")
print(f"   standings:{len(standings)} first5:{len(first5_stats)} pitcher_wl:{len(pitcher_wl)}")
print(f"   statcast_batters:{len(statcast_batters)} pitch_mix:{len(pitch_mix)}")
