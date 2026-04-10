"""
fetch_mlb_stats.py  v2.0
Corre via GitHub Actions cada 2 horas.
Genera mlb_stats.json con todos los datos de pybaseball + datos nuevos.
Nuevos en v2: LOB%, QS, F-Strike%, GB%, FB%, FBv, HR/9, bat_side,
              xBA_vsL/vsR, avg_velo_recent, velo_delta, fps_pct,
              batting_recent (14d), pitching_recent (14d)
"""

import json
import warnings
import datetime
warnings.filterwarnings("ignore")

import pybaseball
from pybaseball import (
    batting_stats,
    pitching_stats,
    statcast,
    team_batting,
    team_pitching,
    pitching_stats_range,
    batting_stats_range,
)
import pandas as pd

pybaseball.cache.enable()

SEASON = 2026
TODAY  = datetime.date.today()
START  = f"{SEASON}-03-20"
END    = TODAY.strftime("%Y-%m-%d")

print(f"[fetch_mlb_stats v2] {TODAY}  season={SEASON}  range={START}→{END}")

def safe(val):
    try:
        if val is None: return None
        f = float(val)
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
            rec[c] = safe(row[c]) if pd.api.types.is_numeric_dtype(df[c]) else (str(row[c]) if pd.notna(row[c]) else None)
        out.append(rec)
    return out

# ════ 1. BATTING season (FanGraphs) ════
print("→ batting_stats (FanGraphs)...")
bat_cols = [
    "Name","Team","G","AB","PA","R","H","HR","RBI","BB","SO",
    "AVG","OBP","SLG","OPS","wOBA","wRC+",
    "BB%","K%","ISO","BABIP","Spd",
    "Barrel%","HardHit%","xBA","xOBP","xSLG","EV","WAR",
]
try:
    bat_df = batting_stats(SEASON, qual=50)
    batting = df_to_records(bat_df, bat_cols)
    print(f"   {len(batting)} bateadores")
except Exception as e:
    print(f"   ERROR: {e}"); batting = []

# ════ 2. PITCHING season (FanGraphs) ════
print("→ pitching_stats (FanGraphs)...")
pit_cols = [
    "Name","Team","G","GS","IP","W","L","SV",
    "ERA","FIP","xFIP","WHIP","K/9","BB/9","HR/9",
    "K%","BB%","BABIP","LOB%","GB%","FB%","Hard%","Barrel%",
    "F-Strike%","FBv","QS","WAR",
]
try:
    pit_df = pitching_stats(SEASON, qual=10)
    pitching = df_to_records(pit_df, pit_cols)
    print(f"   {len(pitching)} pitchers")
except Exception as e:
    print(f"   ERROR: {e}"); pitching = []

# ════ 3. STATCAST últimos 7d ════
print("→ statcast (últimos 7 días)...")
start_7d = (TODAY - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
try:
    sc_df = statcast(start_dt=start_7d, end_dt=END)
    print(f"   {len(sc_df)} pitches raw")

    # 3a. Pitch mix por pitcher
    sc_sub = sc_df[["pitcher","player_name","pitch_type","release_speed","release_spin_rate"]].dropna(subset=["pitcher"])
    pitch_mix = {}
    for pid, grp in sc_sub.groupby("pitcher"):
        name = grp["player_name"].iloc[0]
        mix  = {}
        total = len(grp)
        for pt, cnt in grp["pitch_type"].value_counts().items():
            sub = grp[grp["pitch_type"] == pt]
            mix[str(pt)] = {
                "pct": round(cnt/total*100, 1),
                "avg_velo": safe(sub["release_speed"].mean()),
                "avg_spin": safe(sub["release_spin_rate"].mean()),
            }
        pitch_mix[int(pid)] = {"name": str(name), "mix": mix}
    print(f"   pitch_mix → {len(pitch_mix)} pitchers")

    # 3b. Statcast batter aggregates con platoon splits y bat_side
    sc_bat = sc_df[["batter","player_name","stand","estimated_ba_using_speedangle",
                     "launch_speed","barrel","p_throws"]].dropna(subset=["batter"])
    statcast_batters = []
    for bid, grp in sc_bat.groupby("batter"):
        name = grp["player_name"].iloc[0]
        n    = len(grp)
        bat_side = grp["stand"].mode()[0] if "stand" in grp.columns else None
        rec = {"batter_id": int(bid), "name": str(name), "pitches_seen": n, "bat_side": bat_side}

        xba_col = grp["estimated_ba_using_speedangle"]
        rec["xBA"] = safe(xba_col.mean())
        if "p_throws" in grp.columns:
            vsL = grp[grp["p_throws"]=="L"]["estimated_ba_using_speedangle"]
            vsR = grp[grp["p_throws"]=="R"]["estimated_ba_using_speedangle"]
            rec["xBA_vsL"] = safe(vsL.mean()) if len(vsL)>=5 else None
            rec["xBA_vsR"] = safe(vsR.mean()) if len(vsR)>=5 else None

        if "launch_speed" in grp.columns:
            rec["avg_exit_vel"] = safe(grp["launch_speed"].mean())
            rec["max_exit_vel"] = safe(grp["launch_speed"].max())
            rec["hard_hit_pct"] = safe(len(grp[grp["launch_speed"]>=95])/n*100)
            if "p_throws" in grp.columns:
                rec["ev_vsL"] = safe(grp[grp["p_throws"]=="L"]["launch_speed"].mean())
                rec["ev_vsR"] = safe(grp[grp["p_throws"]=="R"]["launch_speed"].mean())

        if "barrel" in grp.columns:
            rec["barrel_pct"] = safe(grp["barrel"].sum()/n*100)

        statcast_batters.append(rec)
    print(f"   statcast_batters → {len(statcast_batters)} bateadores")

except Exception as e:
    print(f"   ERROR statcast: {e}")
    pitch_mix = {}; statcast_batters = []

# ════ 4. VELO DELTA 30d (señal de fatiga/lesión) ════
print("→ statcast velo 30d (fatiga/lesión)...")
start_30d = (TODAY - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
try:
    sc_30d = statcast(start_dt=start_30d, end_dt=END)
    sc_velo = sc_30d[["pitcher","player_name","release_speed","pitch_type","balls","strikes","game_date"]].dropna(subset=["pitcher","release_speed"])

    for pid, grp in sc_velo.groupby("pitcher"):
        pid_int = int(pid)
        name = grp["player_name"].iloc[0]
        fb_grp = grp[grp["pitch_type"].isin(["FF","SI","FC"])] if "pitch_type" in grp.columns else grp
        avg_velo_30d = safe(fb_grp["release_speed"].mean()) if len(fb_grp)>=10 else None

        grp = grp.copy()
        grp["game_date"] = pd.to_datetime(grp["game_date"])
        cutoff_7d = pd.Timestamp(TODAY) - pd.Timedelta(days=7)
        recent_7d = fb_grp[fb_grp["game_date"] >= cutoff_7d] if "game_date" in fb_grp.columns else pd.DataFrame()
        avg_velo_recent = safe(recent_7d["release_speed"].mean()) if len(recent_7d)>=5 else avg_velo_30d

        velo_delta = round(avg_velo_recent - avg_velo_30d, 2) if (avg_velo_recent and avg_velo_30d) else None

        # First Pitch Strike% (aproximación)
        fps_pct = None
        if "balls" in grp.columns and "strikes" in grp.columns:
            first_pitches = grp[(grp["balls"]==0) & (grp["strikes"]==0)]
            fps_pct = safe(len(first_pitches)/max(len(grp),1)*100) if len(first_pitches)>=10 else None

        if pid_int in pitch_mix:
            pitch_mix[pid_int].update({
                "avg_velo_30d": avg_velo_30d,
                "avg_velo_recent": avg_velo_recent,
                "velo_delta": velo_delta,
                "fps_pct": fps_pct,
            })
        else:
            pitch_mix[pid_int] = {"name": str(name), "mix": {},
                "avg_velo_30d": avg_velo_30d, "avg_velo_recent": avg_velo_recent,
                "velo_delta": velo_delta, "fps_pct": fps_pct}

    print(f"   velo_delta calculado para {len(pitch_mix)} pitchers")
except Exception as e:
    print(f"   ERROR velo 30d: {e}")

# ════ 5. BATTING RECIENTE 14d ════
print("→ batting_stats_range (últimos 14 días)...")
start_14d = (TODAY - datetime.timedelta(days=14)).strftime("%Y-%m-%d")
bat_recent_cols = [
    "Name","Team","G","AB","PA","H","HR","RBI","BB","SO",
    "AVG","OBP","SLG","OPS","wOBA","wRC+","ISO","BABIP",
]
try:
    bat_recent_df = batting_stats_range(start_14d, END)
    batting_recent = df_to_records(bat_recent_df, bat_recent_cols)
    print(f"   {len(batting_recent)} bateadores (14d)")
except Exception as e:
    print(f"   ERROR batting_recent: {e}"); batting_recent = []

# ════ 6. PITCHING RECIENTE 14d ════
print("→ pitching_stats_range (últimos 14 días)...")
pit_recent_cols = [
    "Name","Team","G","GS","IP","W","L",
    "ERA","FIP","WHIP","K/9","BB/9","K%","BB%","LOB%","GB%",
]
try:
    pit_recent_df = pitching_stats_range(start_14d, END)
    pitching_recent = df_to_records(pit_recent_df, pit_recent_cols)
    print(f"   {len(pitching_recent)} pitchers (14d)")
except Exception as e:
    print(f"   ERROR pitching_recent: {e}"); pitching_recent = []

# ════ 7. TEAM BATTING ════
print("→ team_batting...")
try:
    tb_df = team_batting(SEASON)
    team_bat = df_to_records(tb_df, ["Team","G","AVG","OBP","SLG","OPS","wOBA","wRC+","HR","R","BB","SO","WAR"])
    print(f"   {len(team_bat)} equipos")
except Exception as e:
    print(f"   ERROR: {e}"); team_bat = []

# ════ 8. TEAM PITCHING ════
print("→ team_pitching...")
try:
    tp_df = team_pitching(SEASON)
    team_pit = df_to_records(tp_df, ["Team","G","ERA","FIP","xFIP","WHIP","K/9","BB/9","HR/9","IP","WAR"])
    print(f"   {len(team_pit)} equipos")
except Exception as e:
    print(f"   ERROR: {e}"); team_pit = []

# ════ 9. ENSAMBLE FINAL ════
output = {
    "generated_at":    TODAY.isoformat(),
    "season":          SEASON,
    "statcast_window": f"{start_7d} → {END}",
    "recent_window":   f"{start_14d} → {END}",
    "batting":         batting,
    "pitching":        pitching,
    "batting_recent":  batting_recent,
    "pitching_recent": pitching_recent,
    "statcast_batters": statcast_batters,
    "pitch_mix":       pitch_mix,
    "team_batting":    team_bat,
    "team_pitching":   team_pit,
}

with open("mlb_stats.json", "w") as f:
    json.dump(output, f, separators=(",", ":"))

size_kb = len(json.dumps(output)) / 1024
print(f"\n✅ mlb_stats.json v2 generado — {size_kb:.1f} KB")
print(f"   batting: {len(batting)} | pitching: {len(pitching)}")
print(f"   batting_recent: {len(batting_recent)} | pitching_recent: {len(pitching_recent)}")
print(f"   statcast_batters: {len(statcast_batters)} | pitch_mix: {len(pitch_mix)}")
print(f"   team_bat: {len(team_bat)} | team_pit: {len(team_pit)}")
