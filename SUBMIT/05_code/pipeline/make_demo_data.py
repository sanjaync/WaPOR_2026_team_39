#!/usr/bin/env python3
"""
Generate a SYNTHETIC placeholder dataset so the web map runs before any real
WaPOR raster has been downloaded.

    ############################################################
    #  THESE NUMBERS ARE NOT MEASUREMENTS. THEY ARE INVENTED.  #
    #  Every output is stamped data_status="DEMO" and the web  #
    #  map shows a permanent banner until real data replaces   #
    #  it. Do not put these figures in a pitch as fact.        #
    ############################################################

Why it exists: the app, the decision logic and the pitch can all be built and
demoed while someone else does the WaPOR download. Run 03_zonal_stats.py once
you have real GeoTIFFs and this file is superseded automatically.

The values are drawn from plausible published ranges for Egypt so the demo does
not look absurd, and so the *shape* of the result (rice belt = low beneficial
fraction) matches the physical story the concept rests on:

  - Irrigated Nile Delta / Valley seasonal AETI : ~450-800 mm per summer season
  - Beneficial fraction (T / AETI):
        ponded rice          ~0.45-0.58   (open water evaporates all season)
        other Delta crops    ~0.60-0.72
        Nile Valley          ~0.58-0.70
  - Interception is small for these crops: ~1-3% of AETI
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DATA_INTERIM, SEASON_END, SEASON_LABEL, SEASON_START

RNG = np.random.default_rng(20260819)      # fixed seed: the demo is reproducible

# (mean AETI mm/season, sd), (mean beneficial fraction, sd)
PROFILE = {
    "Delta - rice belt": ((735, 45), (0.515, 0.030)),
    "Delta - other":     ((640, 40), (0.665, 0.030)),
    "Nile Valley":       ((690, 55), (0.640, 0.035)),
}


def main() -> None:
    gdf = gpd.read_file(DATA_INTERIM / "governorates.geojson")

    aeti, bf = [], []
    for system in gdf["system"]:
        (a_mu, a_sd), (b_mu, b_sd) = PROFILE[system]
        aeti.append(RNG.normal(a_mu, a_sd))
        bf.append(np.clip(RNG.normal(b_mu, b_sd), 0.35, 0.80))

    gdf["aeti_mm"] = np.round(aeti, 1)
    beneficial_fraction = np.array(bf)

    # Split AETI into its components. I is small; E is the remainder.
    gdf["i_mm"] = np.round(gdf["aeti_mm"] * RNG.uniform(0.010, 0.030, len(gdf)), 1)
    gdf["t_mm"] = np.round(gdf["aeti_mm"] * beneficial_fraction, 1)
    gdf["e_mm"] = np.round(gdf["aeti_mm"] - gdf["t_mm"] - gdf["i_mm"], 1)

    # Irrigated area actually "seen" by the satellite. In reality this comes from
    # counting pixels above the AETI threshold in 03_zonal_stats.py. Here we just
    # assume the reported cultivated area is 88-97% detectable.
    gdf["irrigated_ha"] = np.round(
        gdf["cultivated_ha"] * RNG.uniform(0.88, 0.97, len(gdf)), 0)

    # A confidence proxy. Real version: cloud frequency, L1/L2 agreement,
    # distance to a validated station. Here: larger + more homogeneous = higher.
    score = (np.log10(gdf["irrigated_ha"].clip(lower=1)) / 6.0
             + RNG.uniform(0.0, 0.35, len(gdf)))
    gdf["confidence"] = np.where(score > 0.72, "high",
                          np.where(score > 0.55, "medium", "low"))

    gdf["data_status"] = "DEMO"
    dest = DATA_INTERIM / "zonal_stats.geojson"
    gdf.to_file(dest, driver="GeoJSON")

    meta = {
        "data_status": "DEMO",
        "warning": ("Synthetic placeholder values. Not WaPOR measurements. "
                    "Run pipeline/02_fetch_wapor.py then 03_zonal_stats.py."),
        "season_label": SEASON_LABEL,
        "season_start": SEASON_START,
        "season_end": SEASON_END,
        "generated_by": "pipeline/make_demo_data.py",
    }
    (DATA_INTERIM / "zonal_meta.json").write_text(json.dumps(meta, indent=2))

    print("  !! SYNTHETIC DEMO DATA - not WaPOR measurements !!")
    print(f"  wrote {dest}")
    print(f"\n  {'governorate':<16}{'system':<20}{'AETI':>7}{'E':>7}{'T':>7}{'BF':>7}")
    for _, r in gdf.sort_values("e_mm", ascending=False).iterrows():
        print(f"  {r['gov']:<16}{r['system']:<20}{r['aeti_mm']:>7.0f}"
              f"{r['e_mm']:>7.0f}{r['t_mm']:>7.0f}"
              f"{r['t_mm']/r['aeti_mm']:>7.2f}")


if __name__ == "__main__":
    main()
