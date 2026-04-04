"""
fetch_mlb_stats.py
Corre via GitHub Actions cada 2 horas.
Genera mlb_stats.json con todos los datos de pybaseball.
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
    statcast_pitcher,
    playerid_lookup,
    team_batting,
    team_pitching,
    pitching_stats_range,
)
import pandas as pd

pybaseball.cache.enable()

SEASON = 2026
TODAY  = datetime.date.today()
START  = f"{SEASON}-03-20"
END    = TODAY.strftime("%Y-%m-%d")

print(f"[fetch_mlb_stats] {TODAY}  season={SEASON}  range={START}→{END}")

# ─── helper ──────────────────────────────────────────────────────────────────
def safe(val):
    """Convierte NaN / inf a None para JSON."""
    try:
        if val is None:
            return None
        f = float(val)
        import math
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 3)
    except (TypeError, ValueError):
        return str(val) if val else None

def df_to_records(df, cols):
    """Extrae columnas existentes y convierte a lista de dicts JSON-safe."""
    available = [c for c in cols if c in df.columns]
    missing   = [c for c in cols if c not in df.columns]
    if missing:
        print(f"  ⚠ columnas no encontradas: {missing}")
    out = []
    for _, row in df[available].iterrows():
        rec = {}
        for c in available:
            rec[c] = safe(row[c]) if pd.api.types.is_numeric_dtype(df[c]) else (str(row[c]) if pd.notna(row[c]) else None)
        out.append(rec)
    return out

# ═══════════════════════════════════════════════════════════════════════════
# 1. BATTING — season stats por bateador (FanGraphs)
#    team_avg, OBP, SLG, wOBA, wRC+, AB, R, H, RBI, HR, BB, K, OPS
# ═══════════════════════════════════════════════════════════════════════════
print("→ batting_stats (FanGraphs)...")
bat_cols = [
    "Name", "Team", "G", "AB", "R", "H", "HR", "RBI", "BB", "SO",
    "AVG", "OBP", "SLG", "OPS", "wOBA", "wRC+",
    "Barrel%", "HardHit%", "xBA", "xOBP", "xSLG", "EV",   # Statcast cols (FG los incluye desde ~2015)
    "WAR",
]
try:
    bat_df = batting_stats(SEASON, qual=50)   # mínimo 50 PA
    batting = df_to_records(bat_df, bat_cols)
    print(f"   {len(batting)} bateadores")
except Exception as e:
    print(f"   ERROR: {e}")
    batting = []

# ═══════════════════════════════════════════════════════════════════════════
# 2. PITCHING — season stats por pitcher (FanGraphs)
#    ERA, FIP, xFIP, WHIP, K/9, BB/9
# ═══════════════════════════════════════════════════════════════════════════
print("→ pitching_stats (FanGraphs)...")
pit_cols = [
    "Name", "Team", "G", "GS", "IP", "W", "L", "SV",
    "ERA", "FIP", "xFIP", "WHIP", "K/9", "BB/9",
    "K%", "BB%", "BABIP", "LOB%",
    "Hard%", "Barrel%",
    "WAR",
]
try:
    pit_df = pitching_stats(SEASON, qual=10)  # mínimo 10 IP
    pitching = df_to_records(pit_df, pit_cols)
    print(f"   {len(pitching)} pitchers")
except Exception as e:
    print(f"   ERROR: {e}")
    pitching = []

# ═══════════════════════════════════════════════════════════════════════════
# 3. STATCAST — últimos 7 días
#    xBA, hard_hit%, barrel%, exit_velocity, launch_angle
#    pitch_velocity, spin_rate, pitch_type (pitch_mix)
# ═══════════════════════════════════════════════════════════════════════════
print("→ statcast (últimos 7 días)...")
start_7d = (TODAY - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
try:
    sc_df = statcast(start_dt=start_7d, end_dt=END)
    print(f"   {len(sc_df)} pitches raw")

    # ── 3a. Pitch mix por pitcher ─────────────────────────────────────────
    pitch_mix_cols = [
        "pitcher", "player_name", "pitch_type",
        "release_speed", "release_spin_rate",
        "pfx_x", "pfx_z",
    ]
    available_sc = [c for c in pitch_mix_cols if c in sc_df.columns]
    sc_sub = sc_df[available_sc].dropna(subset=["pitcher"])

    pitch_mix = {}
    for pid, grp in sc_sub.groupby("pitcher"):
        name = grp["player_name"].iloc[0] if "player_name" in grp.columns else str(pid)
        mix  = {}
        total = len(grp)
        if "pitch_type" in grp.columns:
            for pt, cnt in grp["pitch_type"].value_counts().items():
                entry = {"pct": round(cnt / total * 100, 1)}
                if "release_speed" in grp.columns:
                    sub = grp[grp["pitch_type"] == pt]
                    entry["avg_velo"]  = safe(sub["release_speed"].mean())
                    entry["avg_spin"]  = safe(sub["release_spin_rate"].mean()) if "release_spin_rate" in sub.columns else None
                mix[str(pt)] = entry
        pitch_mix[int(pid)] = {"name": str(name), "mix": mix}
    print(f"   pitch_mix → {len(pitch_mix)} pitchers")

    # ── 3b. Statcast batter aggregates (xBA, barrel, EV) ─────────────────
    batter_cols = [
        "batter", "player_name",
        "estimated_ba_using_speedangle",   # xBA
        "launch_speed",                    # exit velocity
        "launch_angle",
        "barrel",
        "hit_distance_sc",
    ]
    available_bat = [c for c in batter_cols if c in sc_df.columns]
    sc_bat = sc_df[available_bat].dropna(subset=["batter"])

    statcast_batters = []
    for bid, grp in sc_bat.groupby("batter"):
        name = grp["player_name"].iloc[0] if "player_name" in grp.columns else str(bid)
        n    = len(grp)
        rec  = {"batter_id": int(bid), "name": str(name), "pitches_seen": n}
        if "estimated_ba_using_speedangle" in grp.columns:
            rec["xBA"] = safe(grp["estimated_ba_using_speedangle"].mean())
        if "launch_speed" in grp.columns:
            rec["avg_exit_vel"]  = safe(grp["launch_speed"].mean())
            rec["max_exit_vel"]  = safe(grp["launch_speed"].max())
            hard = grp[grp["launch_speed"] >= 95] if "launch_speed" in grp.columns else pd.DataFrame()
            rec["hard_hit_pct"]  = safe(len(hard) / n * 100) if n else None
        if "barrel" in grp.columns:
            barrels = grp["barrel"].sum()
            rec["barrel_pct"] = safe(barrels / n * 100) if n else None
        statcast_batters.append(rec)
    print(f"   statcast_batters → {len(statcast_batters)} bateadores")

except Exception as e:
    print(f"   ERROR statcast: {e}")
    pitch_mix        = {}
    statcast_batters = []

# ═══════════════════════════════════════════════════════════════════════════
# 4. TEAM BATTING — promedios por equipo (team_avg, OBP, SLG…)
# ═══════════════════════════════════════════════════════════════════════════
print("→ team_batting...")
team_bat_cols = ["Team", "G", "AVG", "OBP", "SLG", "OPS", "wOBA", "wRC+", "HR", "R", "BB", "SO", "WAR"]
try:
    tb_df = team_batting(SEASON)
    team_bat = df_to_records(tb_df, team_bat_cols)
    print(f"   {len(team_bat)} equipos")
except Exception as e:
    print(f"   ERROR: {e}")
    team_bat = []

# ═══════════════════════════════════════════════════════════════════════════
# 5. TEAM PITCHING
# ═══════════════════════════════════════════════════════════════════════════
print("→ team_pitching...")
team_pit_cols = ["Team", "G", "ERA", "FIP", "xFIP", "WHIP", "K/9", "BB/9", "HR/9", "IP", "WAR"]
try:
    tp_df = team_pitching(SEASON)
    team_pit = df_to_records(tp_df, team_pit_cols)
    print(f"   {len(team_pit)} equipos")
except Exception as e:
    print(f"   ERROR: {e}")
    team_pit = []

# ═══════════════════════════════════════════════════════════════════════════
# 6. ENSAMBLE FINAL
# ═══════════════════════════════════════════════════════════════════════════
output = {
    "generated_at":       TODAY.isoformat(),
    "season":             SEASON,
    "statcast_window":    f"{start_7d} → {END}",
    "batting":            batting,           # bateadores individuales (FanGraphs)
    "pitching":           pitching,          # pitchers individuales (FanGraphs)
    "statcast_batters":   statcast_batters,  # xBA, EV, barrel% (Statcast)
    "pitch_mix":          pitch_mix,         # velocidad, spin, mix por pitcher
    "team_batting":       team_bat,          # stats por equipo
    "team_pitching":      team_pit,          # stats pitching por equipo
}

with open("mlb_stats.json", "w") as f:
    json.dump(output, f, separators=(",", ":"))

size_kb = len(json.dumps(output)) / 1024
print(f"\n✅ mlb_stats.json generado — {size_kb:.1f} KB")
print(f"   batting: {len(batting)} | pitching: {len(pitching)}")
print(f"   statcast_batters: {len(statcast_batters)} | pitch_mix: {len(pitch_mix)}")
print(f"   team_bat: {len(team_bat)} | team_pit: {len(team_pit)}")
