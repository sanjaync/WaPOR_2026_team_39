# Data sources

Every number in this project traces to one of the following. If it is not listed
here, it is not in the app.

## 1. WaPOR v3 — FAO

The evapotranspiration data. Level 2 = 100 m, dekadal (10-day).

| Variable | Meaning | Why we use it |
|---|---|---|
| `AETI` | Actual evapotranspiration + interception | Total water consumed; also our cropland mask |
| `E` | **Evaporation** | Water lost without growing anything — the whole concept |
| `T` | Transpiration | Water that actually grew a crop |
| `I` | Interception | Small; kept for completeness of the balance |
| `RET` | Reference ET | Not used here; useful for adequacy/deficit indicators |

Access routes, in order of convenience:

1. **`wapordl`** (what `02_fetch_wapor.py` uses)
   ```bash
   pip install wapordl
   ```
   Requires the GDAL Python bindings, which require the GDAL C library:
   - Ubuntu/Debian: `sudo apt install -y libgdal-dev gdal-bin`
   - macOS: `brew install gdal`
   - easiest overall: `conda install -c conda-forge gdal wapordl`

2. **WaPOR portal** — https://wapor.apps.fao.org
   Draw the AOI, pick the mapset, export GeoTIFF. Save into
   `data/raw/wapor/<VAR>/` and `03_zonal_stats.py` will find them.

3. **Google Earth Engine** — the collections are not in the GEE search catalogue
   but resolve by id: `projects/UNFAO/wapor/v3/L2-AETI-D`, `.../L2-E-D`, and so
   on. Export to Drive, then drop the GeoTIFFs in `data/raw/wapor/`.

> Note: FAO domains are blocked from some sandboxes and CI runners. That is why
> step 02 is deliberately separable from the rest of the pipeline.

## 2. IPAT — the upstream tool

**Irrigation assessment tool for Egypt**, operational pilot hosted by the Ministry
of Water Resources and Irrigation. WaPOR v3 Level 3 (20 m), Middle and West Delta,
~1.5 million ha, three irrigation systems. Partners: MWRI, scheme managers, policy
makers, IWMI, with IHE Delft and FAO.
https://zemamipa.streamlit.app/

This project is designed to sit **downstream of IPAT**: IPAT identifies high and
low productivity areas; this layer converts that into a budget allocation. Sibling
tools worth referencing in the pitch: **IRWI** (Egypt irrigation-scheduling app,
under development, Nile Delta) and the **Gezira** dashboard in Sudan, which shows
the same pattern at scheme level.

## 3. Administrative boundaries

Natural Earth 10 m admin-1 (public domain), filtered to Egypt.
https://github.com/nvkelso/natural-earth-vector

Governorates are coarser than the command areas a scheme manager works with. They
were chosen because a *national budget allocation* is made at roughly this level,
and because they are freely redistributable. Swap in MWRI irrigation-directorate
or markaz (ADM2) boundaries when you can get them — only the display labels in
`config.py` assume governorate level.

## 4. Cultivated area

`config.py: CULTIVATED_KFEDDAN`. **Approximate planning figures, not official
statistics.** Order of magnitude and relative ranking are right; the individual
numbers are not sourced. Replace with the MALR / CAPMAS *Agricultural Statistics
Bulletin* cropped-area table before any figure leaves the team.

Note that `03_zonal_stats.py` also derives an *observed* irrigated area by
counting pixels above the AETI threshold. Comparing the two is a free sanity
check, and a nice slide: satellite-observed irrigated area vs. reported
cultivated area.

## 5. Intervention costs

See `docs/ASSUMPTIONS.md`. These are the weakest numbers in the project and are
treated as such: editable in the UI, flagged in the brief, listed in the footer.

## 6. Protocol

Indicator definitions follow **WaPORIPA**, the standardised irrigation performance
assessment protocol for WaPOR v3.
https://github.com/wateraccounting/WaPORIPA
