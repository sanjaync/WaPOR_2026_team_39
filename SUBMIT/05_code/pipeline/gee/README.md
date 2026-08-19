# Earth Engine route

Three scripts. Two of them are the app; the third is the fallback.

| File | What it's for |
|---|---|
| `01_zonal_to_asset.js` | Computes per-governorate seasonal statistics once and writes them to an Earth Engine **asset**. Run this first. |
| `02_app.js` | The published app. Reads that asset and runs the whole allocation client-side. |
| `wapor_export.js` | Exports the four seasonal rasters to Drive, for the local Python pipeline. Only needed if you want the offline HTML build. |

---

## Why an asset, not Drive

The app needs **one row per governorate**, not eighteen dekads of 100 m raster.
Computing that on every page load would take 30–60 seconds and spend a compute
quota per visitor. Computing it once into an asset makes the app open in under a
second, and the allocation maths — ranking, budget, equity floor — is then plain
arithmetic on twenty rows, so sliders respond instantly with no server round-trip.

## Run order

1. Open `01_zonal_to_asset.js`, set `EE_USER` to your Earth Engine username
   (Assets tab), press **Run**.
2. **Read the printed diagnostics before you export.** In particular:
   - 18 dekads per variable
   - the governorate name list — GAUL transliterates differently ("Al Buhayrah"
     for Beheira), and `NAME_MAP` at the top is where you fix mismatches
   - the system classification (rice belt / Delta / Valley) — check the northern
     Delta governorates landed in the rice belt
   - AETI roughly 450–800 mm in the Delta, beneficial fraction roughly 0.5–0.8
   - total irrigated area in the region of 3.5–4.0 Mha for Egypt
3. Tasks tab → run the single export (2–5 min).
4. Open `02_app.js`, paste the asset path into `ASSET_ID`, press **Run**.
5. Apps → **Publish** → New App → Public. The URL works for anyone; viewers do
   not need a Google account.

## Keep the two implementations in step

`02_app.js` and `pipeline/04_rank_and_allocate.py` implement the *same*
allocator — greedy cheapest-water-first, one measure per governorate, an equity
floor spread by irrigated area, and an area-proportional comparator. The
intervention table is duplicated in `02_app.js` and `pipeline/config.py`.

**If you change one, change both.** A live demo that disagrees with the
repository is worse than no live demo, and it is the kind of thing a jury finds
by accident.

## What the app gives up

Worth knowing before you rely on it in the pitch.

- **Plain widgets.** Earth Engine's UI is labels, buttons, sliders and charts.
  No custom CSS. The standalone HTML build looks considerably better.
- **It needs the network.** If venue wifi fails during your pitch, the app is a
  blank screen and `webmap/index.html` is not. Record the video from the HTML
  build and keep the app as the shareable link.
- **It cannot run inside a ministry firewall.** Fine for a prototype, a real
  limitation for the adoption story. Say so if asked rather than being caught.
