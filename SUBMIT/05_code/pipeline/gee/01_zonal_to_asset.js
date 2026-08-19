/**
 * STEP 1 of 2 — precompute per-governorate statistics into an Earth Engine asset.
 * WaPOR Hackathon 2026 · Team 39 · "Same Budget, More Water"
 *
 * WHY THIS EXISTS
 *   The app (02_app.js) needs one number per governorate, not 18 dekads of
 *   100 m rasters. If the app computed that on every page load it would take
 *   30-60 s and burn a compute quota per visitor. Computing it ONCE into an
 *   asset makes the app load in under a second and cost almost nothing.
 *
 * HOW TO RUN
 *   1. code.earthengine.google.com -> paste -> Run
 *   2. Read the printed diagnostics. Check the governorate names and the
 *      system classification are sane before you trust anything.
 *   3. Tasks tab -> RUN the single export task (~2-5 min)
 *   4. Copy the printed asset path into 02_app.js
 *
 * VERIFIED 19 Aug 2026: scale property is 0.1, DN x 0.1 = mm/DAY.
 */

// ------------------------------------------------------------------ config
var SEASON_START = '2024-05-01';
var SEASON_END   = '2024-11-01';          // exclusive; May-Oct = 18 dekads
var SEASON_LABEL = 'Summer (Nili/Sefi) 2024';
var SCALE        = 100;                    // m, native WaPOR L2
var VARIABLES    = ['AETI', 'E', 'T', 'I'];

// EDIT THIS: your Earth Engine username, from the Assets tab.
var EE_USER      = 'ee-sanjayet';
var ASSET_ID     = 'projects/' + EE_USER + '/assets/wapor_t39_zonal_2024';

// Cropland / open-water thresholds. Same values as pipeline/config.py — if you
// change one, change both, or the app and the Python pipeline will disagree.
var AETI_THRESHOLD_MM      = 200;   // below this, not irrigated
var MIN_BENEFICIAL_FRACTION = 0.15; // T/AETI below this is open water, not a crop

// ------------------------------------------------------- boundaries
// FAO GAUL level 1 = governorates. GAUL's transliterations differ from the ones
// used in the pitch ("Al Buhayrah" vs "Beheira"), so we relabel. The script
// prints every name it finds — check that list before trusting the output.
var govs = ee.FeatureCollection('FAO/GAUL/2015/level1')
             .filter(ee.Filter.eq('ADM0_NAME', 'Egypt'));

var NAME_MAP = ee.Dictionary({
  'Al Buhayrah': 'Beheira',        'Kafr-El-Sheikh': 'Kafr El Sheikh',
  'Ad Daqahliyah': 'Dakahlia',     'Ash Sharqiyah': 'Sharqia',
  'Al Gharbiyah': 'Gharbia',       'Al Minufiyah': 'Menoufia',
  'Al Qalyubiyah': 'Qalyubia',     'Dumyat': 'Damietta',
  'Al Iskandariyah': 'Alexandria', 'Bur Sa`id': 'Port Said',
  'Al Isma`iliyah': 'Ismailia',    'Al Fayyum': 'Fayoum',
  'Bani Suwayf': 'Beni Suef',      'Al Minya': 'Minya',
  'Asyut': 'Assiut',               'Suhaj': 'Sohag',
  'Qina': 'Qena',                  'Al Uqsur': 'Luxor',
  'Aswan': 'Aswan',                'Al Jizah': 'Giza'
});

// Rice belt = the northern Delta, where ponded paddy evaporates all season.
var RICE_BELT = ['Kafr El Sheikh','Beheira','Dakahlia','Damietta','Sharqia'];
var DELTA     = RICE_BELT.concat(['Gharbia','Menoufia','Qalyubia','Alexandria',
                                  'Port Said','Ismailia']);

govs = govs.map(function (f) {
  var raw = f.get('ADM1_NAME');
  var nm  = ee.String(ee.Algorithms.If(NAME_MAP.contains(raw), NAME_MAP.get(raw), raw));
  var sys = ee.Algorithms.If(ee.List(RICE_BELT).contains(nm), 'Delta - rice belt',
            ee.Algorithms.If(ee.List(DELTA).contains(nm),     'Delta - other',
                                                              'Nile Valley'));
  return f.set({gov: nm, system: sys});
});

// ------------------------------------------------------- seasonal sums
function seasonalSum(varName) {
  var col = ee.ImageCollection('projects/UNFAO/wapor/v3/L2-' + varName + '-D')
              .filterDate(SEASON_START, SEASON_END);

  var perDekad = col.map(function (img) {
    var start = ee.Date(img.get('system:time_start'));
    // Dekads are 10, 10, then 8-11 days. Never hardcode this.
    var days  = ee.Number(ee.Algorithms.If(
      img.propertyNames().contains('system:time_end'),
      ee.Date(img.get('system:time_end')).difference(start, 'day'), 10));
    // Scale property is 0.1 and converts DN to mm/DAY, so the day count is
    // what turns it into mm/dekad. Both steps are required.
    var scale = ee.Number(ee.Algorithms.If(
      img.propertyNames().contains('scale'), img.get('scale'), 1));
    // .toFloat() is mandatory: a per-image day count makes GEE infer a
    // different value range per image and .sum() rejects the collection.
    return img.select(0).multiply(scale).multiply(days)
              .toFloat().rename(varName);
  });
  return ee.ImageCollection(perDekad).sum().toFloat().rename(varName)
           .set('n_dekads', col.size());
}

var S = {};
VARIABLES.forEach(function (v) { S[v] = seasonalSum(v); });

// ------------------------------------------------------- cropland mask
// Open water first: JRC permanent surface water, plus a physical filter.
// The northern Delta lakes sit inside our top-ranked governorates, so leaving
// them in would manufacture the very result this project claims to find.
var notWater = ee.Image('JRC/GSW1_4/GlobalSurfaceWater')
                 .select('occurrence').gt(50).unmask(0).not();

var bf = S.T.divide(S.AETI.max(1));         // beneficial fraction
var cropMask = S.AETI.gt(AETI_THRESHOLD_MM)
                 .and(bf.gt(MIN_BENEFICIAL_FRACTION))
                 .and(notWater);

// ------------------------------------------------------- zonal statistics
var stack = S.AETI.addBands(S.E).addBands(S.T).addBands(S.I)
              .addBands(ee.Image.pixelArea().divide(1e4).rename('irrigated_ha'))
              .updateMask(cropMask);

// mean gives the mm values; sum gives the hectares. sharedInputs applies both
// reducers to every band, so we simply pick the ones we want afterwards.
var zonal = stack.reduceRegions({
  collection: govs,
  reducer: ee.Reducer.mean().combine({reducer2: ee.Reducer.sum(), sharedInputs: true}),
  scale: SCALE,
  tileScale: 4
});

zonal = zonal.map(function (f) {
  var aeti = ee.Number(ee.Algorithms.If(f.get('AETI_mean'), f.get('AETI_mean'), 0));
  var e    = ee.Number(ee.Algorithms.If(f.get('E_mean'),    f.get('E_mean'),    0));
  var t    = ee.Number(ee.Algorithms.If(f.get('T_mean'),    f.get('T_mean'),    0));
  var i    = ee.Number(ee.Algorithms.If(f.get('I_mean'),    f.get('I_mean'),    0));
  var ha   = ee.Number(ee.Algorithms.If(f.get('irrigated_ha_sum'),
                                        f.get('irrigated_ha_sum'), 0));
  return ee.Feature(f.geometry(), {
    gov: f.get('gov'), system: f.get('system'),
    aeti_mm: aeti, e_mm: e, t_mm: t, i_mm: i,
    irrigated_ha: ha,
    beneficial_fraction: ee.Number(ee.Algorithms.If(aeti.gt(0), t.divide(aeti), 0)),
    // non-beneficial evaporation, Mm3 per season: mm x ha x 10 m3/mm/ha / 1e6
    nonben_mcm: e.multiply(ha).multiply(10).divide(1e6),
    season: SEASON_LABEL
  });
}).filter(ee.Filter.gt('irrigated_ha', 1000));   // drop desert-only units

// ------------------------------------------------------- diagnostics
print('=== CHECK THESE BEFORE RUNNING THE EXPORT ===');
print('dekads found per variable (expect 18):',
      ee.Dictionary.fromLists(VARIABLES,
        VARIABLES.map(function (v) { return S[v].get('n_dekads'); })));
print('governorates kept:', zonal.size());
print('names + system classification — fix NAME_MAP above if any look wrong:',
      zonal.reduceColumns(ee.Reducer.toList(2), ['gov','system']).get('list'));
print('AETI mm/season by governorate (expect roughly 450-800 in the Delta):',
      zonal.reduceColumns(ee.Reducer.toList(2), ['gov','aeti_mm']).get('list'));
print('beneficial fraction by governorate (expect ~0.5-0.8):',
      zonal.reduceColumns(ee.Reducer.toList(2), ['gov','beneficial_fraction']).get('list'));
print('total non-beneficial evaporation, Mm3/season:',
      zonal.aggregate_sum('nonben_mcm'));
print('total irrigated ha (Egypt is roughly 3.5-4.0 million ha in total):',
      zonal.aggregate_sum('irrigated_ha'));

Map.centerObject(zonal, 6);
Map.addLayer(S.E.updateMask(cropMask), {min: 40, max: 260,
  palette: ['ffffff','fde3d5','f0a684','eb6834','9c3a15']}, 'E mm/season');
Map.addLayer(ee.Image().paint(zonal, 0, 2), {palette: ['000000']}, 'governorates');

// ------------------------------------------------------- export
Export.table.toAsset({
  collection: zonal,
  description: 'wapor_t39_zonal_2024',
  assetId: ASSET_ID
});
print('After the task finishes, put this in 02_app.js:', ASSET_ID);
