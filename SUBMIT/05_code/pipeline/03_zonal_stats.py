#!/usr/bin/env python3
"""
Step 03 - turn WaPOR dekadal rasters into per-governorate seasonal statistics.

Input : data/raw/wapor/{AETI,E,T,I}/*.tif   (dekadal, mm/dekad, from step 02)
Output: data/interim/zonal_stats.geojson    (same schema as make_demo_data.py)

Method
------
1. Sum the dekadal rasters over the season -> mm per season for each variable.
2. Mask to irrigated cropland.

   The mask is the nice part. In Egypt you do not need a land-cover product:
   outside the irrigated Nile system, seasonal AETI collapses to near zero
   because there is no water and essentially no rain. A seasonal AETI threshold
   therefore separates irrigated land from desert almost perfectly, using the
   same data we are already analysing and adding no extra dependency or
   licence. AETI_THRESHOLD_MM is deliberately conservative.

3. Zonal-average each variable over the masked pixels per governorate, and count
   masked pixels to get the irrigated area actually observed from space (which is
   an independent check on the reported cultivated-area statistics).
"""
import json
import math
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (DATA_INTERIM, DATA_RAW, SEASON_END, SEASON_LABEL,
                    SEASON_START)

WAPOR_DIR = DATA_RAW / "wapor"
AETI_THRESHOLD_MM = 200.0     # seasonal; below this we call the pixel non-irrigated
# May-Oct inclusive is 18 dekads. Kept as a set to tolerate a season edge.
EXPECTED_DEKADS = {17, 18, 19}
# Open water evaporates all season and would masquerade as high-E cropland.
# The northern Delta lakes (Burullus, Manzala, Idku, Maryut) and Lake Qarun in
# Fayoum sit inside our top-ranked governorates, so this is not optional.
# T/AETI below this is physically impossible for a crop -> it is open water.
MIN_BENEFICIAL_FRACTION = 0.15
VARIABLES = ["AETI", "E", "T", "I"]


def seasonal_sum(var: str):
    """Sum every dekadal GeoTIFF for `var` into one seasonal mm raster."""
    tifs = sorted((WAPOR_DIR / var).rglob("*.tif"))
    if not tifs:
        return None, None
    total, profile = None, None
    for fp in tifs:
        with rasterio.open(fp) as src:
            arr = src.read(1, masked=True).astype("float32")
            nodata = src.nodata
            if nodata is not None:
                arr = np.ma.masked_equal(arr, nodata)
            arr = np.ma.masked_less(arr, 0)      # WaPOR uses negatives as flags
            # Fill with NaN, not 0. A cloud-gap dekad filled with zero silently
            # lowers the seasonal total and can push a real field below the
            # cropland threshold, reclassifying irrigated land as desert.
            filled = arr.filled(np.nan)
            if total is None:
                total, profile = filled, src.profile
            else:
                total = np.nansum(np.dstack([total, filled]), axis=2)
    profile.update(dtype="float32", count=1, nodata=np.nan)
    print(f"    {var}: {len(tifs)} dekads summed")
    if len(tifs) not in EXPECTED_DEKADS:
        print(f"    WARNING: expected {sorted(EXPECTED_DEKADS)} dekads for this "
              f"season, found {len(tifs)}. Stale downloads in the folder, or a "
              "partial fetch, will corrupt the seasonal total.")
    return total, profile


def main() -> None:
    if not WAPOR_DIR.exists() or not any(WAPOR_DIR.rglob("*.tif")):
        sys.exit(
            f"No WaPOR GeoTIFFs found in {WAPOR_DIR}.\n"
            "Run pipeline/02_fetch_wapor.py on a machine that can reach FAO,\n"
            "or run pipeline/make_demo_data.py to work with synthetic placeholders."
        )

    print(f"  season: {SEASON_LABEL}")
    seasonal, profile = {}, None
    for var in VARIABLES:
        arr, prof = seasonal_sum(var)
        if arr is None:
            sys.exit(f"Missing rasters for {var} in {WAPOR_DIR / var}")
        seasonal[var] = arr
        profile = profile or prof

    # Persist the seasonal composites - useful for QA and for the pitch visuals
    comp_dir = DATA_INTERIM / "seasonal"
    comp_dir.mkdir(parents=True, exist_ok=True)
    for var, arr in seasonal.items():
        with rasterio.open(comp_dir / f"{var}_seasonal.tif", "w", **profile) as dst:
            dst.write(arr.astype("float32"), 1)

    gdf = gpd.read_file(DATA_INTERIM / "governorates.geojson")
    ref = rasterio.open(comp_dir / "AETI_seasonal.tif")
    gdf = gdf.to_crs(ref.crs)

    # Pixel area. WaPOR v3 GeoTIFFs are delivered in EPSG:4326, so the raster
    # transform is in DEGREES, not metres. Multiplying the two degree steps and
    # dividing by 10,000 yields square degrees / 10,000 - a number around 1e-10,
    # which silently drives every irrigated_ha to zero and empties the whole
    # allocation. Handle both geographic and projected inputs explicitly.
    if ref.crs and ref.crs.is_geographic:
        lat = (ref.bounds.bottom + ref.bounds.top) / 2.0
        m_per_deg_lat = 111_132.0
        m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat))
        px_area_ha = abs(ref.transform.a * m_per_deg_lon
                         * ref.transform.e * m_per_deg_lat) / 10_000.0
    else:
        px_area_ha = abs(ref.transform.a * ref.transform.e) / 10_000.0
    print(f"  pixel area: {px_area_ha:.4f} ha "
          f"({'geographic' if ref.crs and ref.crs.is_geographic else 'projected'} CRS)")
    if not (0.05 < px_area_ha < 25):
        sys.exit(f"Implausible pixel area ({px_area_ha} ha). Check the raster CRS "
                 "and transform before trusting anything downstream.")

    rows = []
    for _, feat in gdf.iterrows():
        stats = {}
        for var in VARIABLES:
            with rasterio.open(comp_dir / f"{var}_seasonal.tif") as src:
                clip, _ = rio_mask(src, [feat.geometry], crop=True, filled=True,
                                   nodata=np.nan)
            stats[var] = clip[0]

        with np.errstate(invalid="ignore", divide="ignore"):
            bf_px = stats["T"] / np.where(stats["AETI"] > 0, stats["AETI"], np.nan)
        irrigated = (stats["AETI"] > AETI_THRESHOLD_MM) & (bf_px > MIN_BENEFICIAL_FRACTION)
        n_px = int(np.nansum(irrigated))
        if n_px == 0:
            rows.append(dict(aeti_mm=0.0, e_mm=0.0, t_mm=0.0, i_mm=0.0,
                             irrigated_ha=0.0, confidence="low"))
            continue

        means = {v: float(np.nanmean(stats[v][irrigated])) for v in VARIABLES}

        # Confidence: how much of the polygon is confidently irrigated, and how
        # variable AETI is within it. Wide spread -> mixed signal -> lower trust.
        cv = float(np.nanstd(stats["AETI"][irrigated]) / max(means["AETI"], 1e-6))
        conf = "high" if (n_px > 20_000 and cv < 0.35) else \
               "medium" if (n_px > 4_000 and cv < 0.55) else "low"

        rows.append(dict(
            aeti_mm=round(means["AETI"], 1),
            e_mm=round(means["E"], 1),
            t_mm=round(means["T"], 1),
            i_mm=round(means["I"], 1),
            irrigated_ha=round(n_px * px_area_ha, 0),
            confidence=conf,
        ))

    ref.close()
    for key in ("aeti_mm", "e_mm", "t_mm", "i_mm", "irrigated_ha", "confidence"):
        gdf[key] = [r[key] for r in rows]
    gdf["data_status"] = "WAPOR"
    gdf = gdf.to_crs(4326)

    dest = DATA_INTERIM / "zonal_stats.geojson"
    gdf.to_file(dest, driver="GeoJSON")
    (DATA_INTERIM / "zonal_meta.json").write_text(json.dumps({
        "data_status": "WAPOR",
        "source": "FAO WaPOR v3 Level 2 (100 m), dekadal",
        "season_label": SEASON_LABEL,
        "season_start": SEASON_START,
        "season_end": SEASON_END,
        "cropland_mask": f"seasonal AETI > {AETI_THRESHOLD_MM} mm",
        "generated_by": "pipeline/03_zonal_stats.py",
    }, indent=2))

    print(f"\n  wrote {dest}")
    print(f"  observed irrigated area: {gdf['irrigated_ha'].sum()/1e6:.2f} Mha "
          f"(reported cultivated: {gdf['cultivated_ha'].sum()/1e6:.2f} Mha)")


if __name__ == "__main__":
    main()
