/**
 * STEP 2 of 2 — the Earth Engine App.
 * WaPOR Hackathon 2026 · Team 39 · "Same Budget, More Water"
 *
 * WHAT IT DOES
 *   Reads the precomputed asset from 01_zonal_to_asset.js, then runs the whole
 *   allocation CLIENT-SIDE. Moving a slider re-ranks instantly with no server
 *   round-trip, because the maths is arithmetic on twenty rows, not raster work.
 *
 * HOW TO PUBLISH
 *   1. Paste into code.earthengine.google.com, set ASSET_ID below, press Run
 *   2. Check the panel populates, then Apps -> Publish -> New App
 *   3. Set it Public. The URL works for anyone, no Google account needed.
 *
 * WHAT TO SAY ABOUT IT
 *   The point is not that it is a map. The point is that it hands a planning
 *   officer an ORDERED SPENDING LIST, and that next season the same instrument
 *   can check whether the money worked.
 */

// EDIT: the asset written by 01_zonal_to_asset.js
var ASSET_ID = 'projects/ee-sanjayet/assets/wapor_t39_zonal_2024';
var SEASON   = 'Summer (Nili/Sefi) 2024';

// ------------------------------------------------------- intervention model
// Literature-order ESTIMATES, not measurements. Editable here and in
// pipeline/config.py — keep the two in step or the app and the Python
// pipeline will quietly disagree.
var INTERVENTIONS = [
  {key:'laser', label:'Laser land levelling', usd_ha:75, life:5, red:0.10, seasons:2,
   applies:['Delta - rice belt','Delta - other','Nile Valley'],
   note:'Already deployed at scale in Egypt, so cost and effect are the best constrained of the four.'},
  {key:'awd', label:'Alternate wetting & drying', usd_ha:25, life:1, red:0.10, seasons:1,
   applies:['Delta - rice belt'],
   note:'Evaporation component ONLY. AWD\'s headline saving is percolation, which the Delta largely reuses downstream, so we exclude it.'},
  {key:'mulch', label:'Straw / plastic mulching', usd_ha:260, life:1, red:0.30, seasons:1,
   applies:['Delta - other','Nile Valley'],
   note:'Suppressed evaporation can become transpiration and yield rather than saved water. Upper bound.'},
  {key:'drip', label:'Drip retrofit', usd_ha:1800, life:10, red:0.45, seasons:2,
   applies:['Delta - other','Nile Valley'],
   note:'Largest saving, largest capital cost. Not viable for paddy rice.'}
];

var NILE='#0b3c5d', EVAP='#d96f32', BLUE='#2a78d6', MUTE='#6b7b87';
var RAMP = ['#ffffff','#cde2fb','#6da7ec','#2a78d6','#0b3c5d'];

var METRICS = {
  'Evaporation (mm/season)':      {p:'e_mm',               ramp:['#ffffff','#fde3d5','#f0a684','#eb6834','#9c3a15']},
  'Recoverable volume (Mm3)':     {p:'nonben_mcm',         ramp:RAMP},
  'Beneficial fraction (T/AETI)': {p:'beneficial_fraction',ramp:['#9c3a15','#eb6834','#f0a684','#cde2fb','#2a78d6']},
  'Cost of saved water (USD/m3)': {p:'usd_per_m3',         ramp:RAMP}
};

// ------------------------------------------------------- state
var D = [];                 // client-side rows, filled by evaluate()
var budget = 12e6, equity = 0, metric = 'Evaporation (mm/season)';
var fc = ee.FeatureCollection(ASSET_ID);

// ------------------------------------------------------- the allocator
// Identical logic to pipeline/04_rank_and_allocate.py. If you change one,
// change both — a demo that disagrees with the repo is worse than no demo.
function buildOptions() {
  var out = [];
  D.forEach(function (d) {
    INTERVENTIONS.forEach(function (iv) {
      if (iv.applies.indexOf(d.system) === -1) return;
      if (!(d.irrigated_ha > 0) || !(d.e_mm > 0)) return;
      // recoverable water, m3/YEAR — seasons matter: laser levelling and drip
      // persist through the winter season, AWD and mulching do not.
      var rec  = d.e_mm * d.irrigated_ha * 10 * iv.red * iv.seasons;
      var cost = (iv.usd_ha / iv.life) * d.irrigated_ha;      // USD/year
      if (rec <= 0) return;
      out.push({gov:d.gov, system:d.system, iv:iv, ha:d.irrigated_ha,
                rec:rec, cost:cost, upm3:cost/rec});
    });
  });
  out.sort(function (a, b) { return a.upm3 - b.upm3; });
  return out;
}

function allocate(opts, b, floor) {
  floor = floor || 0;
  var bestOf = {};
  opts.forEach(function (o) { if (!(o.gov in bestOf)) bestOf[o.gov] = o; });

  var funded = {};
  // Reserved share, spread across EVERY governorate by irrigated area. This
  // exists because pure cheapest-first funds four districts out of twenty, and
  // no ministry with an equity mandate signs that.
  var reserved = b * floor;
  if (reserved > 0) {
    var totHa = 0;
    D.forEach(function (d) { if (bestOf[d.gov]) totHa += d.irrigated_ha; });
    if (totHa > 0) D.forEach(function (d) {
      var o = bestOf[d.gov]; if (!o) return;
      funded[d.gov] = Math.min(reserved * d.irrigated_ha / totHa, o.cost);
    });
  }
  var remaining = b;
  Object.keys(funded).forEach(function (k) { remaining -= funded[k]; });

  opts.forEach(function (o) {
    if (remaining <= 0) return;
    if (bestOf[o.gov] !== o) return;               // one measure per governorate
    var head = o.cost - (funded[o.gov] || 0);
    if (head <= 0) return;
    var take = Math.min(head, remaining);
    funded[o.gov] = (funded[o.gov] || 0) + take;
    remaining -= take;
  });

  var picks = [], spent = 0, saved = 0;
  Object.keys(funded).forEach(function (g) {
    if (funded[g] <= 0) return;
    var o = bestOf[g], frac = funded[g] / o.cost;
    spent += funded[g]; saved += o.rec * frac;
    picks.push({gov:g, iv:o.iv, funded:funded[g], frac:frac,
                saved:o.rec * frac, ha:o.ha * frac, upm3:o.upm3});
  });
  picks.sort(function (a, b2) { return a.upm3 - b2.upm3; });
  return {picks:picks, spent:spent, saved:saved};
}

// The comparator: same budget split by irrigated area. A NEUTRAL PRIOR — what
// you would do knowing only where the cropland is — not a claim about what the
// ministry currently does, for which we have no citation.
function allocateAreaProportional(opts, b) {
  var bestOf = {}, totHa = 0;
  opts.forEach(function (o) { if (!(o.gov in bestOf)) bestOf[o.gov] = o; });
  D.forEach(function (d) { if (bestOf[d.gov]) totHa += d.irrigated_ha; });
  var spent = 0, saved = 0;
  D.forEach(function (d) {
    var o = bestOf[d.gov]; if (!o || totHa <= 0) return;
    var give = Math.min(b * d.irrigated_ha / totHa, o.cost);
    spent += give; saved += o.rec * (give / o.cost);
  });
  return {spent:spent, saved:saved};
}

// ------------------------------------------------------- UI
var fmt  = function (n, d) { return n.toFixed(d === undefined ? 1 : d); };
var usd  = function (n) { return n >= 1e6 ? '$' + fmt(n/1e6, 2) + 'M' : '$' + Math.round(n).toLocaleString(); };

var panel = ui.Panel({style:{width:'420px', padding:'14px', backgroundColor:'#ffffff'}});
var listPanel = ui.Panel();
var kpiPanel  = ui.Panel();

panel.add(ui.Label('Same Budget, More Water',
  {fontSize:'24px', fontWeight:'bold', color:NILE, margin:'0 0 2px 0'}));
panel.add(ui.Label('Team 39 · WaPOR Hackathon 2026 · from tools to decisions',
  {fontSize:'11px', color:MUTE, margin:'0 0 10px 0'}));
panel.add(ui.Label(
  'WaPOR reports evaporation and transpiration separately. Transpiration grew a ' +
  'crop; evaporation was delivered, paid for, and grew nothing. This ranks every ' +
  'governorate by how much of that evaporated water is recoverable, and what it ' +
  'costs to recover — so a fixed budget buys the most water rather than the most ' +
  'even-looking map.',
  {fontSize:'12px', color:'#14202a', margin:'0 0 12px 0'}));

var status = ui.Label('Loading ' + SEASON + ' …', {fontSize:'12px', color:EVAP});
panel.add(status);

var metricSelect = ui.Select({
  items: Object.keys(METRICS), value: metric, style:{width:'380px', margin:'6px 0'},
  onChange: function (v) { metric = v; drawMap(); }
});
panel.add(ui.Label('Map layer', {fontSize:'11px', fontWeight:'bold', color:MUTE, margin:'8px 0 0 0'}));
panel.add(metricSelect);

var budgetLabel = ui.Label('Budget: $12.0M', {fontSize:'14px', fontWeight:'bold', color:NILE, margin:'10px 0 0 0'});
panel.add(budgetLabel);
panel.add(ui.Slider({min:1, max:80, value:12, step:1, style:{width:'380px'},
  onChange: function (v) { budget = v * 1e6; budgetLabel.setValue('Budget: $' + fmt(v) + 'M'); render(); }}));

var equityLabel = ui.Label('Equity floor: none', {fontSize:'14px', fontWeight:'bold', color:NILE, margin:'8px 0 0 0'});
panel.add(equityLabel);
panel.add(ui.Slider({min:0, max:100, value:0, step:5, style:{width:'380px'},
  onChange: function (v) {
    equity = v / 100;
    equityLabel.setValue('Equity floor: ' + (v === 0 ? 'none' : v + '%'));
    render();
  }}));
panel.add(ui.Label(
  'The equity floor is the share of the budget spread across every governorate ' +
  'by area before the rest is targeted. Pure cheapest-first funds four out of ' +
  'twenty; this prices the political constraint instead of ignoring it.',
  {fontSize:'11px', color:MUTE, margin:'2px 0 8px 0'}));

panel.add(kpiPanel);
panel.add(ui.Label('Recommended spending order', {fontSize:'13px', fontWeight:'bold', color:NILE, margin:'10px 0 4px 0'}));
panel.add(listPanel);

panel.add(ui.Label('What this does not claim', {fontSize:'12px', fontWeight:'bold', color:EVAP, margin:'14px 0 2px 0'}));
panel.add(ui.Label(
  'Evaporation saved on-field is not automatically water saved at basin scale — ' +
  'some returns to a drain or the aquifer and is reused downstream, and ' +
  'suppressing evaporation can convert it to transpiration and yield rather than ' +
  'to saved water. Recoverable evaporation is an UPPER BOUND. ETLook\'s E/T split ' +
  'is also least constrained over standing water, which is exactly where this ' +
  'signal is. These figures rank places against each other; they are not a water ' +
  'account. Intervention costs are literature-order estimates, so the ranking is ' +
  'robust and the magnitude is soft.',
  {fontSize:'10px', color:MUTE}));

ui.root.clear();
var map = ui.Map();
map.setOptions('SATELLITE');
map.style().set('cursor', 'crosshair');
ui.root.add(ui.SplitPanel({firstPanel:panel, secondPanel:map}));

// ------------------------------------------------------- render
function render() {
  var opts = buildOptions();
  if (!opts.length) { status.setValue('No options — check the asset.'); return; }
  var r    = allocate(opts, budget, equity);
  var pure = allocate(opts, budget, 0);
  var base = allocateAreaProportional(opts, budget);
  var gain = base.saved > 0 ? (r.saved / base.saved - 1) * 100 : 0;

  kpiPanel.clear();
  kpiPanel.add(ui.Label((gain >= 0 ? '+' : '') + fmt(gain, 0) + '%',
    {fontSize:'34px', fontWeight:'bold', color:EVAP, margin:'6px 0 0 0'}));
  kpiPanel.add(ui.Label('more water than an area-proportional split of the same budget',
    {fontSize:'11px', color:MUTE, margin:'0 0 6px 0'}));
  kpiPanel.add(ui.Label(
    fmt(r.saved/1e6, 0) + ' Mm³ recovered  ·  ' + usd(r.spent) + ' spent  ·  $' +
    fmt(r.spent/r.saved, 3) + '/m³  ·  ' + r.picks.length + ' governorates funded',
    {fontSize:'12px', color:'#14202a'}));
  if (equity > 0) kpiPanel.add(ui.Label(
    'Equity floor of ' + fmt(equity*100, 0) + '% funds ' + r.picks.length +
    ' governorates and costs ' + fmt((1 - r.saved/pure.saved)*100, 1) +
    '% of the water versus pure targeting.',
    {fontSize:'11px', color:EVAP}));

  listPanel.clear();
  r.picks.slice(0, 10).forEach(function (p, i) {
    var row = ui.Panel({layout:ui.Panel.Layout.flow('horizontal'),
                        style:{margin:'0', padding:'2px 0'}});
    row.add(ui.Label(String(i+1), {fontSize:'12px', color:MUTE, margin:'0 6px 0 0'}));
    row.add(ui.Label(p.gov, {fontSize:'12px', fontWeight:'bold', color:NILE, margin:'0 6px 0 0'}));
    row.add(ui.Label(p.iv.label, {fontSize:'11px', color:MUTE, margin:'0 6px 0 0'}));
    row.add(ui.Label(usd(p.funded) + ' → ' + fmt(p.saved/1e6) + ' Mm³',
      {fontSize:'11px', color:'#14202a', margin:'0'}));
    listPanel.add(row);
  });

  drawFunded(r.picks.map(function (p) { return p.gov; }));
}

function drawMap() {
  map.layers().reset();
  var m = METRICS[metric];
  // usd_per_m3 is client-side only, so push it back as a property when needed.
  var painted = ee.Image().float().paint(scored(), m.p);
  var vals = D.map(function (d) { return d[m.p]; }).filter(function (v) { return v > 0; });
  vals.sort(function (a, b) { return a - b; });
  var lo = vals[0], hi = vals[vals.length - 1];
  map.addLayer(painted, {min:lo, max:hi, palette:m.ramp}, metric);
  map.addLayer(ee.Image().paint(fc, 0, 1), {palette:['#ffffff']}, 'boundaries');
  render();
}

// Re-attach the client-computed USD/m3 so the map can colour by it.
function scored() {
  var opts = buildOptions(), best = {};
  opts.forEach(function (o) { if (!(o.gov in best)) best[o.gov] = o.upm3; });
  var feats = D.map(function (d) {
    return ee.Feature(null, {gov:d.gov, usd_per_m3: best[d.gov] || 0});
  });
  var lut = ee.FeatureCollection(feats);
  var join = ee.Join.inner().apply(fc, lut,
    ee.Filter.equals({leftField:'gov', rightField:'gov'}));
  return join.map(function (f) {
    return ee.Feature(ee.Feature(f.get('primary')).geometry())
             .copyProperties(ee.Feature(f.get('primary')))
             .copyProperties(ee.Feature(f.get('secondary')), ['usd_per_m3']);
  });
}

function drawFunded(names) {
  var existing = map.layers().length();
  if (existing > 2) map.layers().remove(map.layers().get(existing - 1));
  var funded = fc.filter(ee.Filter.inList('gov', names));
  map.addLayer(ee.Image().paint(funded, 0, 3), {palette:[EVAP]}, 'funded this budget');
}

// ------------------------------------------------------- load
fc.evaluate(function (data, err) {
  if (err || !data) { status.setValue('Could not read the asset. Check ASSET_ID. ' + (err || '')); return; }
  D = data.features.map(function (f) { return f.properties; });
  D.sort(function (a, b) { return b.e_mm - a.e_mm; });
  var totalNonBen = D.reduce(function (s, d) { return s + d.nonben_mcm; }, 0);
  status.setValue(SEASON + ' · WaPOR v3 L2 · ' + D.length + ' governorates · ' +
                  Math.round(totalNonBen).toLocaleString() +
                  ' Mm³ evaporating without growing a crop');
  status.style().set('color', NILE);
  map.centerObject(fc, 6);
  drawMap();
});
