#!/usr/bin/env python3
"""
Step 02 - download WaPOR v3 rasters for the study area.

  >>> RUN THIS ON A MACHINE WITH INTERNET ACCESS TO data.apps.fao.org <<<

FAO's servers are not reachable from every sandbox, so this step is deliberately
separate from the rest of the pipeline. Everything downstream reads GeoTIFFs from
data/raw/wapor/ and does not care how they got there.

Usage
-----
    pip install "wapordl>=1.2"          # needs GDAL: see docs/DATA_SOURCES.md
    python pipeline/02_fetch_wapor.py

Downloads, for the season defined in config.py, WaPOR v3 Level 2 (100 m) dekadal:
    L2-AETI-D  actual evapotranspiration and interception
    L2-E-D     evaporation          <- the layer this whole project turns on
    L2-T-D     transpiration
    L2-I-D     interception

Fallbacks if wapordl will not install (GDAL is the usual culprit):
  a) WaPOR portal   https://wapor.apps.fao.org  - draw the AOI, pick the mapset,
     export GeoTIFF, save into data/raw/wapor/ using the same file naming.
  b) Google Earth Engine - collections are not in the GEE search catalogue but
     resolve by id, e.g. projects/UNFAO/wapor/v3/L2-AETI-D
     Export to Drive, then place the GeoTIFFs in data/raw/wapor/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (DATA_RAW, SEASON_END, SEASON_LABEL, SEASON_START,
                    WAPOR_LEVEL, WAPOR_REGION)

OUT = DATA_RAW / "wapor"
OUT.mkdir(parents=True, exist_ok=True)

# Variables we need. E is the one nobody else uses - it is the whole point.
VARIABLES = ["AETI", "E", "T", "I"]

# Region: a GeoJSON path clips tightly and downloads far less; a country code is
# simpler but pulls the whole of Egypt. Both are accepted by wapordl.
AOI_GEOJSON = Path(__file__).resolve().parents[1] / "data" / "interim" / "governorates.geojson"


def main() -> None:
    try:
        from wapordl import wapor_map
    except ImportError:
        sys.exit(
            "wapordl is not installed.\n"
            "  pip install wapordl\n"
            "It needs the GDAL Python bindings, which need the GDAL C library:\n"
            "  Ubuntu/Debian : sudo apt install -y libgdal-dev gdal-bin\n"
            "  macOS         : brew install gdal\n"
            "  conda (easiest): conda install -c conda-forge gdal wapordl\n"
            "Or use one of the manual fallbacks in this file's docstring."
        )

    region = str(AOI_GEOJSON) if AOI_GEOJSON.exists() else WAPOR_REGION
    period = [SEASON_START, SEASON_END]
    print(f"season : {SEASON_LABEL}  ({SEASON_START} to {SEASON_END})")
    print(f"region : {region}")

    for var in VARIABLES:
        code = f"{WAPOR_LEVEL}-{var}-D"          # D = dekadal
        dest = OUT / var
        dest.mkdir(parents=True, exist_ok=True)
        print(f"\n  {code} -> {dest}")
        try:
            # unit_conversion="dekad" gives mm per dekad rather than mm/day,
            # so a plain sum over the season is already mm/season.
            fp = wapor_map(region, code, period, str(dest),
                           unit_conversion="dekad")
            print(f"    ok: {fp}")
        except Exception as exc:                  # noqa: BLE001 - report and continue
            print(f"    FAILED: {type(exc).__name__}: {exc}")
            print("    (continuing - re-run this step for the missing variable)")

    tifs = sorted(OUT.rglob("*.tif"))
    print(f"\n{len(tifs)} GeoTIFF(s) now in {OUT}")
    if not tifs:
        print("Nothing downloaded. Check network access to data.apps.fao.org, "
              "then see the fallbacks in this file's docstring.")


if __name__ == "__main__":
    main()
