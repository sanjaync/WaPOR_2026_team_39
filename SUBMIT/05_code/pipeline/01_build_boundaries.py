#!/usr/bin/env python3
"""
Step 01 - build the study-area boundary file.

Input : data/raw/ne_10m_admin_1_states_provinces.geojson  (Natural Earth, public domain)
Output: data/interim/governorates.geojson                 (EPSG:4326, simplified)

Natural Earth admin-1 is used because it is public domain and dependency-free.
If you get access to official MWRI irrigation-directorate or markaz (ADM2)
boundaries, drop them in as a replacement - nothing downstream assumes
governorate level except the display labels.
"""
import json
import sys

import geopandas as gpd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import (COUNTRY_A3, CULTIVATED_KFEDDAN, DATA_INTERIM, DATA_RAW,
                    DISPLAY_NAME, FEDDAN_TO_HA, STUDY_GOVERNORATES, SYSTEM_OF)

NE_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
          "master/geojson/ne_10m_admin_1_states_provinces.geojson")
NE_FILE = DATA_RAW / "ne_admin1.geojson"


def main() -> None:
    if not NE_FILE.exists():
        sys.exit(f"Missing {NE_FILE}\n  curl -sSL -o {NE_FILE} {NE_URL}")

    gdf = gpd.read_file(NE_FILE)
    gdf = gdf[gdf["adm0_a3"] == COUNTRY_A3].copy()
    gdf = gdf[gdf["name"].isin(STUDY_GOVERNORATES)].copy()

    missing = set(STUDY_GOVERNORATES) - set(gdf["name"])
    if missing:
        print(f"  WARNING: not found in Natural Earth: {sorted(missing)}")

    # Attributes the rest of the pipeline relies on
    gdf["gov"] = gdf["name"].map(DISPLAY_NAME).fillna(gdf["name"])
    gdf["gov_ar"] = gdf["name_ar"]
    gdf["system"] = gdf["name"].map(SYSTEM_OF)
    gdf["cultivated_kfeddan"] = gdf["name"].map(CULTIVATED_KFEDDAN).fillna(0.0)
    gdf["cultivated_ha"] = gdf["cultivated_kfeddan"] * 1000 * FEDDAN_TO_HA

    # Equal-area CRS for a true governorate footprint (Africa Albers Equal Area)
    aea = ("+proj=aea +lat_1=20 +lat_2=-23 +lat_0=0 +lon_0=25 "
           "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")
    gdf["gov_area_ha"] = gdf.to_crs(aea).geometry.area / 10_000.0

    # Simplify for a small, fast web payload. 0.01 deg ~ 1.1 km - plenty for a
    # governorate-scale choropleth and it keeps the inlined GeoJSON under ~250 kB.
    gdf["geometry"] = gdf.geometry.simplify(0.01, preserve_topology=True)

    keep = ["gov", "gov_ar", "system", "cultivated_kfeddan", "cultivated_ha",
            "gov_area_ha", "geometry"]
    out = gdf[keep].sort_values("gov").reset_index(drop=True)

    dest = DATA_INTERIM / "governorates.geojson"
    out.to_file(dest, driver="GeoJSON")

    size_kb = dest.stat().st_size / 1024
    print(f"  wrote {dest}  ({len(out)} governorates, {size_kb:.0f} kB)")
    print(f"  total cultivated area: {out['cultivated_ha'].sum()/1e6:.2f} Mha "
          f"({out['cultivated_kfeddan'].sum()/1000:.1f} M feddan)")
    for system, grp in out.groupby("system"):
        print(f"    {system:20s} {len(grp):2d} govs  "
              f"{grp['cultivated_ha'].sum()/1e6:.2f} Mha")


if __name__ == "__main__":
    main()
