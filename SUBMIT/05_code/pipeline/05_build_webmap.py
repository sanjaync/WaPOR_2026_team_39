#!/usr/bin/env python3
"""
Step 05 - build the self-contained web map.

Reads webmap/data/districts.geojson + summary.json, inlines them into
webmap/template.html and writes webmap/index.html.

The output is ONE html file with no external requests: the basemap is inline
SVG drawn from the GeoJSON, the data is embedded, the CSS and JS are inline.
It opens by double-click, works offline, and cannot fail on stage because a
CDN is slow. That matters more than it sounds during a live pitch.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import ROOT, WEBMAP_DATA

TEMPLATE = ROOT / "webmap" / "template.html"
OUTPUT = ROOT / "webmap" / "index.html"


def round_geom(geom, nd=3):
    """Round coordinates - 3 dp is ~110 m, far finer than a governorate needs."""
    if isinstance(geom, (int, float)):
        return round(geom, nd)
    return [round_geom(g, nd) for g in geom]


def main() -> None:
    districts = json.loads((WEBMAP_DATA / "districts.geojson").read_text())
    summary = json.loads((WEBMAP_DATA / "summary.json").read_text())

    payload = []
    for f in districts["features"]:
        p = f["properties"]
        payload.append({
            "gov": p["gov"],
            "ar": p.get("gov_ar") or "",
            "sys": p["system"],
            "irr_ha": round(p["irrigated_ha"]),
            "cult_ha": round(p["cultivated_ha"]),
            "aeti": p["aeti_mm"],
            "e": p["e_mm"],
            "t": p["t_mm"],
            "i": p["i_mm"],
            "conf": p["confidence"],
            "dens": round(p["irrigated_ha"] / max(p["gov_area_ha"], 1), 3),
            "geom": round_geom(f["geometry"]["coordinates"]),
            "gtype": f["geometry"]["type"],
        })

    blob = {
        "districts": payload,
        "interventions": summary["assumptions"]["interventions"],
        "meta": summary["meta"],
        "data_status": summary["data_status"],
        "default_budget": summary["budget_usd"],
        "season_label": summary["season_label"],
    }

    html = TEMPLATE.read_text()
    html = html.replace("/*__DATA__*/null",
                        json.dumps(blob, separators=(",", ":"), ensure_ascii=False))
    OUTPUT.write_text(html, encoding="utf-8")

    kb = OUTPUT.stat().st_size / 1024
    print(f"  wrote {OUTPUT}  ({kb:.0f} kB, self-contained)")
    print(f"  data status: {blob['data_status']}")
    print(f"  {len(payload)} governorates embedded")


if __name__ == "__main__":
    main()
