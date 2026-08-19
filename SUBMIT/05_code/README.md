# Same Budget, More Water

**WaPOR Hackathon 2026 · Team 39 · "From tools to decisions"**

Turning WaPOR's evaporation/transpiration split into a ranked spending list for
Egypt's on-farm modernisation budget.

---

## The idea in one paragraph

**IPAT** — the irrigation assessment tool already operating at Egypt's Ministry of
Water Resources and Irrigation, built on WaPOR v3 Level 3 (20 m) across ~1.5 Mha
of the Middle and West Delta — shows *where* water productivity is high and low.
It stops there. A ministry with a fixed annual budget still has to decide *where
to spend*, and today that decision is made by area or by politics, not by
hydrology. This layer closes that gap. WaPOR is one of very few products that
reports **evaporation (E)** and **transpiration (T)** as separate layers.
Transpiration grew a crop; evaporation did not. Rank every district by how much
evaporated water is recoverable and what it costs to recover it, and the ministry
gets an ordered spending list instead of a map — and, because WaPOR sees the same
district next season, the first honest way to check whether the money worked.

**Test the pitch against this sentence:** *Because of this, an MWRI planning
officer will direct this season's modernisation budget to Kafr El Sheikh,
Damietta and Beheira first, instead of splitting it evenly across governorates.*

---

## Quick start

```bash
pip install -r requirements.txt
./run_all.sh                 # or: ./run_all.sh 25000000  for a $25M budget
open webmap/index.html
```

With no WaPOR rasters present this runs on **synthetic demo data** and says so
loudly, in a red banner, on every screen. Nothing is silently faked.

---

## Getting real WaPOR data in

```bash
# on a machine that can reach data.apps.fao.org
pip install wapordl                    # needs GDAL - see docs/DATA_SOURCES.md
python3 pipeline/02_fetch_wapor.py     # downloads L2 100 m dekadal AETI, E, T, I
python3 pipeline/03_zonal_stats.py     # real zonal statistics
python3 pipeline/04_rank_and_allocate.py
python3 pipeline/05_build_webmap.py
```

The red demo banner disappears by itself once `data_status` flips to `WAPOR`.

---

## Layout

```
MIRO_BOARD.md             board fill + the 1-minute pitch script
VIDEO_STORYBOARD.md       shot-by-shot for the Phase 1 video
pipeline/
  config.py               everything tunable: study area, season, cost model
  01_build_boundaries.py  Natural Earth admin-1 -> study-area GeoJSON
  02_fetch_wapor.py       WaPOR v3 download            [needs FAO access]
  03_zonal_stats.py       rasters -> per-district seasonal E / T / I / AETI
  make_demo_data.py       synthetic stand-in for 02+03  [clearly flagged]
  04_rank_and_allocate.py THE DECISION STEP - ranking, costing, allocation
  05_build_webmap.py      inlines data into a single self-contained HTML
  gee/wapor_export.js     Earth Engine alternative to step 02 - no GDAL needed,
                          and masks the northern Delta lakes at source
webmap/
  template.html           the app (CSS + JS inline, no CDN, works offline)
  index.html              built output - this is what you demo
docs/
  DATA_SOURCES.md         where every number comes from
  ASSUMPTIONS.md          what we assumed and how wrong it could be
```

---

## How the decision is computed

```
recoverable water   V = E_mm × irrigated_ha × 10 × reduction_fraction   [m³]
annualised cost     C = (USD/ha ÷ life_years) × irrigated_ha            [USD/yr]
cost of water       c = C / V                                           [USD/m³]
```

Sort every (district × intervention) pair by `c` ascending, then spend the budget
down that list. The baseline it is compared against splits the same budget by
irrigated area — which is what happens today.

The cropland mask deserves a note. In Egypt you do not need a land-cover product:
outside the irrigated Nile system there is no water and effectively no rain, so
seasonal AETI collapses to near zero. A seasonal AETI threshold therefore
separates irrigated land from desert almost perfectly, using data we are already
analysing, with no extra dependency or licence.

---

## Interventions modelled

| Measure | USD/ha | Life | Evaporation avoided | Applies to |
|---|---:|---:|---:|---|
| Laser land levelling | 75 | 5 yr | 10% | all — **the measure the model actually picks** |
| Alternate wetting & drying | 25 | 1 yr | 10% | rice belt only |
| Straw / plastic mulching | 260 | 1 yr | 30% | non-rice — never selected at any budget |
| Drip retrofit | 1 800 | 10 yr | 45% | non-rice — never selected at any budget |

All four are **editable live in the web map**. Change a number and the ranking,
the allocation and the headline recalculate. This is deliberate: these are
literature-order estimates, not measurements, and the honest move is to expose
them rather than bury them.

---

## What the demo shows

At a $12M budget, targeting recovers about **23% more water than an
area-proportional split** — same money, same measures, different order.

Two results matter more than that headline:

**With evaporation held spatially flat, targeting gains exactly zero.** The whole
advantage is spatial. About 8 of the 23 points need genuine satellite *detail*;
the rest a coarse agronomic classification would give you. We ran that
counterfactual on ourselves and report it in `summary.json["counterfactuals"]`,
because a juror will ask and it is better to have the number first.

**Reserving 25% of the budget as an equity floor funds all twenty governorates
and costs only 3.9% of the water.** Pure cheapest-first funds four. No ministry
with an equity mandate signs the second; almost any would sign the first. Pricing
the political constraint is more useful than optimising around it.

---

## Honest limitations

1. Intervention costs and reduction fractions are estimates. The ranking is
   sensitive to them.
2. Cultivated-area figures in `config.py` are approximate planning numbers, not
   CAPMAS/MALR statistics. Replace before publishing.
3. **On-field evaporation saved is not automatically basin-scale water saved.**
   Some returns to drains and aquifers and is reused downstream; suppressing
   evaporation can also convert it to transpiration and yield rather than to
   saved water. Recoverable E is an *upper bound*. These figures are for
   prioritisation, not water accounting.
6. **ETLook's E/T split is least constrained over standing water** — which is
   exactly where our signal is. No rebuttal; disclose it.
7. **The baseline is a neutral prior, not observed practice.** We have no
   citation for how MWRI actually splits this budget.
4. Administrative polygons contain large desert areas. The map hatches those and
   the statistics describe only the irrigated fraction inside them.
5. Governorates are coarser than the scheme/command-area level IPAT works at.
   Swap in irrigation-directorate boundaries when available — nothing downstream
   assumes governorate level.
