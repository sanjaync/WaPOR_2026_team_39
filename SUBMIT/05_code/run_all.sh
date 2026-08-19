#!/usr/bin/env bash
# End-to-end rebuild. Usage: ./run_all.sh [budget_usd]
set -e
cd "$(dirname "$0")"
BUDGET="${1:-12000000}"

echo "== 01 boundaries =="
python3 pipeline/01_build_boundaries.py

echo "== 02/03 WaPOR data =="
if ls data/raw/wapor/*/*.tif >/dev/null 2>&1; then
  python3 pipeline/03_zonal_stats.py
else
  echo "   no WaPOR rasters found -> using synthetic DEMO data"
  echo "   (run pipeline/02_fetch_wapor.py on a machine that can reach FAO)"
  python3 pipeline/make_demo_data.py
fi

echo "== 04 rank & allocate =="
python3 pipeline/04_rank_and_allocate.py "$BUDGET"

echo "== 05 build web map =="
python3 pipeline/05_build_webmap.py

echo
echo "Done. Open webmap/index.html in a browser."
