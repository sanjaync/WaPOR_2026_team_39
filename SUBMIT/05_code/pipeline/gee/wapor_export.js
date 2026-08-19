/**
 * WaPOR v3 seasonal export — Google Earth Engine
 * WaPOR Hackathon 2026 · Team 39 · "Same Budget, More Water"
 *
 * Use this instead of pipeline/02_fetch_wapor.py when wapordl will not install
 * (GDAL is the usual reason) or when FAO's servers are unreachable.
 *
 * HOW TO RUN
 *   1. Open https://code.earthengine.google.com  (sign in; a free non-commercial
 *      account is enough — registration takes a few minutes)
 *   2. Paste this whole file into the code editor and press Run
 *   3. Open the "Tasks" tab on the right and click RUN on each of the four exports
 *   4. Files land in Google Drive / WaPOR_Team39. Download them into
 *        wapor-app/data/raw/wapor/AETI/ , /E/ , /T/ , /I/
 *   5. python3 pipeline/03_zonal_stats.py && python3 pipeline/04_rank_and_allocate.py
 *      && python3 pipeline/05_build_webmap.py
 *
 * NOTE ON THE COLLECTIONS
 *   WaPOR v3 is not in GEE's searchable catalogue but resolves by id.
 *   Level 2 = 100 m, dekadal (10-day).
 *
 *   BAND NAMING: each image has exactly one band, named after the collection
 *   ('L2-AETI-D', 'L2-E-D', ...), NOT 'band1'. Selecting by name therefore fails
 *   with "Band pattern 'band1' did not match any bands". We select by INDEX -
 *   .select(0) - which is correct for every variable and survives any future
 *   rename by FAO.
 *
 *   Values are stored scaled; the scale factor is read from the image property
 *   rather than hardcoded, because it differs between variables.
 */

// ---------------------------------------------------------------- parameters
var SEASON_START = '2024-05-01';      // summer (Nili/Sefi) season
var SEASON_END   = '2024-11-01';      // exclusive
var SCALE        = 100;               // m — matches WaPOR L2
var FOLDER       = 'WaPOR_Team39';

// Study area: Nile Delta + Valley. Generous bbox; 03_zonal_stats.py clips to
// the governorate polygons anyway.
var AOI = ee.Geometry.Rectangle([29.0, 22.0, 34.5, 31.8]);

var VARIABLES = ['AETI', 'E', 'T', 'I'];

// Set to a number (e.g. 0.1) to force a scale factor, or leave null to read it
// from the image property. Decide this from the RAW diagnostic printed below -
// do not guess, and do not leave it wrong: it multiplies every result.
var SCALE_OVERRIDE = null;

// ------------------------------------------------------------------ helpers
/**
 * Sum a dekadal WaPOR collection over the season.
 *
 * WaPOR dekadal rasters are stored as mm/day averaged over the dekad, NOT as
 * mm/dekad. Summing them raw therefore under-counts by roughly a factor of ten
 * and the error is uneven, because dekads are 10, 10, or 8-11 days long.
 * Multiply each image by its own day count first. This is the same correction
 * that wapordl's unit_conversion="dekad" applies.
 */
function seasonalSum(varName) {
  var col = ee.ImageCollection('projects/UNFAO/wapor/v3/L2-' + varName + '-D')
              .filterDate(SEASON_START, SEASON_END)
              .filterBounds(AOI);

  var perDekad = col.map(function (img) {
    // Days in this dekad. Dekads are 10, 10, or 8-11 days long, so this cannot
    // be hardcoded. Fall back to 10 if the asset lacks system:time_end.
    var start = ee.Date(img.get('system:time_start'));
    var days  = ee.Number(ee.Algorithms.If(
      img.propertyNames().contains('system:time_end'),
      ee.Date(img.get('system:time_end')).difference(start, 'day'),
      10));

    // apply the stored scale factor if present, else assume already physical
    var scale = SCALE_OVERRIDE !== null ? ee.Number(SCALE_OVERRIDE)
              : ee.Number(ee.Algorithms.If(
                  img.propertyNames().contains('scale'), img.get('scale'), 1));

    return img.select(0)            // by index: the band is 'L2-AETI-D' etc, not 'band1'
              .multiply(scale)        // -> mm/day
              .multiply(days)         // -> mm over this dekad
              // BOTH of these are required, and neither is optional:
              //   .toFloat()  - multiplying by a per-image day count (10, 10, 8-11)
              //                 makes GEE infer a DIFFERENT value range for every
              //                 image, and .sum() then rejects the collection as
              //                 heterogeneous ("Mismatched type for band ...
              //                 Expected Float<0.0, 229.5>, actual Float<0.0, 255.0>").
              //                 An explicit cast pins one type for all 18 images.
              //   .rename()   - so the summed images carry identical band names and
              //                 can be combined downstream without another mismatch.
              .toFloat()
              .rename(varName)
              .copyProperties(img, ['system:time_start']);
  });

  return ee.ImageCollection(perDekad).sum()
           .toFloat()
           .rename(varName)
           .set('variable', varName)
           .set('season_start', SEASON_START)
           .set('season_end', SEASON_END)
           .set('n_dekads', col.size());
}

// -------------------------------------------------- open-water / lake mask
/**
 * THE LAKE PROBLEM.
 *
 * The top-ranked governorates (Kafr El Sheikh, Damietta, Dakahlia) all border
 * Lake Burullus and Lake Manzala. Open water evaporates freely all season, so
 * lake pixels inflate E and would make those governorates look like better
 * investment targets than they are. Since they are the headline recommendation,
 * this is the single most damaging unmasked error in the analysis.
 *
 * JRC Global Surface Water gives permanent water occurrence 1984-2021.
 * Occurrence > 50% = water present more than half the time = not cropland.
 */
var gsw = ee.Image('JRC/GSW1_4/GlobalSurfaceWater');
var waterMask = gsw.select('occurrence').gt(50).unmask(0).not();   // 1 = keep

// A second guard: WaPOR itself. On open water, transpiration is ~0 while total
// ET is high, so an extremely low T/AETI ratio flags water bodies the JRC layer
// missed (new aquaculture ponds, for instance, which the Delta has many of).
function lowTranspirationMask(aeti, t) {
  // Both are cast to float above, so this division is type-safe.
  var bf = t.toFloat().divide(aeti.toFloat().max(1));   // guard div-by-zero
  return bf.gt(0.15);                // 1 = keep; below 0.15 is almost certainly water
}

// ------------------------------------------------------------------- export
var seasonal = {};
VARIABLES.forEach(function (v) { seasonal[v] = seasonalSum(v); });

var keep = waterMask.and(lowTranspirationMask(seasonal.AETI, seasonal.T));

VARIABLES.forEach(function (v) {
  var img = seasonal[v].updateMask(keep).clip(AOI).toFloat();

  Export.image.toDrive({
    image: img,
    description: 'WaPOR_L2_' + v + '_seasonal',
    folder: FOLDER,
    fileNamePrefix: v + '_seasonal',
    region: AOI,
    scale: SCALE,
    crs: 'EPSG:4326',
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF'
  });
});

// ------------------------------------------------------------ quick look
Map.centerObject(AOI, 6);
Map.addLayer(seasonal.AETI.updateMask(keep), {min: 0, max: 900,
  palette: ['ffffff', 'cde2fb', '6da7ec', '2a78d6', '0d366b']}, 'AETI mm/season');
Map.addLayer(seasonal.E.updateMask(keep), {min: 0, max: 400,
  palette: ['ffffff', 'fde3d5', 'f0a684', 'eb6834', '9c3a15']}, 'E mm/season', false);
Map.addLayer(waterMask.not().selfMask(), {palette: ['ff0000']}, 'masked open water', false);

// ---- diagnostics ----------------------------------------------------------
// reduceRegion returns a Dictionary, which the console renders as a collapsed
// "Object (1 property)". Pull the value out with .get() so the number prints
// inline - a diagnostic you have to click to read is a diagnostic that gets
// skipped.
var deltaCheck = ee.Geometry.Rectangle([30.4, 30.6, 31.6, 31.4]);  // central Delta

function meanOver(img, bandName) {
  return ee.Number(img.reduceRegion({
    reducer: ee.Reducer.mean(), geometry: deltaCheck, scale: 300, maxPixels: 1e10
  }).get(bandName));
}

var probe = ee.Image(ee.ImageCollection('projects/UNFAO/wapor/v3/L2-AETI-D')
              .filterDate(SEASON_START, SEASON_END).first());

print('--- 1. ASSET STRUCTURE ---------------------------------------------');
print('band names (expect [L2-AETI-D]):', probe.bandNames());
print('scale property (null = none set):', probe.get('scale'));

print('--- 2. SCALE FACTOR CHECK ------------------------------------------');
print('RAW mean of ONE AETI dekad over the central Delta, no scaling:',
      meanOver(probe.select(0), probe.bandNames().get(0)));
// VERIFIED 2026-08-19 on the real asset: the scale property IS 0.1, and WaPOR
// stores dekadal AETI as DN where DN x 0.1 = mm/DAY. Multiplying by the ~10-day
// dekad length then very nearly cancels the 0.1, so the raw DN happens to read
// as mm/dekad. That coincidence makes the raw number a BAD test on its own -
// it looks plausible whether or not the scale was applied. Judge by the
// SEASONAL total in section 3 instead, which does separate the two cases.
print('   raw DN x 0.1 = mm/day; x ~10 days = mm/dekad, so raw DN ~= mm/dekad.');
print('   Do not decide from this number alone - use MEAN AETI below.');

print('--- 3. SEASONAL TOTALS ---------------------------------------------');
VARIABLES.forEach(function (v) {
  print(v + ' dekads found (expect 18):', seasonal[v].get('n_dekads'));
});
var aetiM = meanOver(seasonal.AETI.updateMask(keep), 'AETI');
var eM    = meanOver(seasonal.E.updateMask(keep),    'E');
var tM    = meanOver(seasonal.T.updateMask(keep),    'T');
print('MEAN AETI, mm/season (expect 450-800):', aetiM);
print('MEAN E,    mm/season:', eM);
print('MEAN T,    mm/season:', tM);
// OBSERVED on the real asset over this box: E/AETI = 0.22, T/AETI = 0.78.
// Higher beneficial fraction than the demo data assumed - the central Delta is
// a dense, well-watered canopy, and this box is its best part. Two upward
// biases to keep in mind: the box excludes the lakes and the desert margins,
// and the BF>0.15 open-water filter removes low-BF pixels by construction.
// Expect the study-area figure to sit BELOW this once the full AOI is used.
print('E / AETI   (observed 0.22 here; >0.8 would mean lakes are still in):',
      eM.divide(aetiM));
print('T / AETI   (beneficial fraction; observed 0.78 in the central Delta):',
      tM.divide(aetiM));

print('--- 4. WHAT TO DO --------------------------------------------------');
print('AETI ~450-800 and E/AETI ~0.15-0.45 -> good. Open Tasks, run the 4 exports.');
print('AETI ~50    -> day-count correction failed; everything is 10x low.');
print('AETI ~5000  -> scale applied twice, or SCALE_OVERRIDE set when it should be null.');
print('E/AETI >0.8 -> open-water mask not working; do NOT export, the lakes will');
print('               manufacture the result we are pitching.');

