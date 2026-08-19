# Assumptions, and how wrong they could be

Ranked by how much damage they would do if wrong. A jury will find these; better
that we find them first.

---

## 1. Intervention costs and evaporation-reduction fractions
**Confidence: low. Impact: high — this drives the entire ranking.**

| Measure | USD/ha | Life | E avoided | Comment |
|---|---:|---:|---:|---|
| Laser land levelling | 75 | 5 yr | 10% | Widely deployed in Egypt already, so cost and effect are the best constrained of the four. Reduces ponding depth and over-irrigation of high spots. Credited for 2 seasons/year. |
| Alternate wetting & drying | 25 | 1 yr | 10% | **Corrected down from 25%.** AWD's headline saving in the literature is in water *applied* — percolation and seepage — not in evapotranspiration. In the closed, high-reuse Delta, percolation is largely recovered downstream, so we exclude it and count only the evaporation component: removing the free water surface for part of the season. 1 season/year. |
| Straw / plastic mulching | 260 | 1 yr | 30% | Suppresses bare-soil evaporation between rows. Never selected at any budget we tested. |
| Drip retrofit | 1 800 | 10 yr | 45% | Best saving, worst capital cost. Never selected at any budget we tested. Not viable for paddy. |

**Mitigation.** Every one of these is a live input in the web map. Open the
"Assumptions" panel during the pitch and change one — showing that the ranking is
robust to plausible variation (or admitting where it is not) is far stronger than
claiming precision. Do this *before* someone asks.

**Correction — a claim we previously made and had to withdraw.** An earlier version
of this file said that if alternate wetting and drying cost 3× more than assumed
it would still lead. That was **wrong**. On the original coefficients AWD's
break-even against laser levelling sat at an evaporation reduction of about
0.167, and at 2× cost the recommendation already flipped. We only found this by
adversarially testing our own model, which is why the coefficient has since been
corrected on physical grounds (see AWD row above) and laser levelling is now the
recommended measure across the board.

**What is actually robust.** The *ranking of places* is stable, because it is
driven by observed evaporation, which varies about twofold across the study area.
The *size of the prize* is not stable — it moves with every coefficient in the
table. Present the ranking with confidence and the magnitude as a range.

**Two of the four measures are never selected** at any budget between $6M and
$80M. Mulching and drip are in the model for completeness, not because they do
any work. Do not present them as if they were options under consideration.

---

## 2. Evaporation saved on-field ≠ water saved in the basin
**Confidence: this is certainly true. Impact: high — it bounds the claim.**

Water that evaporates is genuinely lost to the basin. But not all of what a
measure "saves" was evaporating: some of the water an intervention frees up was
already returning to a drain or the aquifer and being reused downstream. In a
closed basin like the Nile Delta, reuse is high, so **basin-scale savings are
smaller than field-scale savings**.

We report *recoverable non-beneficial evaporation*, which is the right quantity
for **prioritisation** — ranking places against each other. It is the wrong
quantity for **water accounting**. Do not let the two get conflated, and say so
first. Frame the output as "where to spend," never as "how much water Egypt will
gain."

---

## 3. Cultivated-area figures
**Confidence: low. Impact: medium.**

`config.py: CULTIVATED_KFEDDAN` is approximate. Relative ranking between
governorates is about right, absolute values are not sourced. Since recoverable
volume scales linearly with area, errors here propagate directly into Mm³.

**Mitigation.** `03_zonal_stats.py` derives irrigated area independently by
counting WaPOR pixels above the AETI threshold. Once real data is loaded, the
reported figures stop mattering — the satellite figure is used instead.

---

## 3b. Two effects that bound the claim from above
**Confidence: both are real. Impact: high on magnitude, none on ranking.**

**E-to-T compensation.** Suppressing bare-soil evaporation often does not reduce
total ET at all: the crop takes up the conserved soil water and transpires it,
converting E into T and yield. That is a good agronomic outcome and a *zero*
water-volume outcome. Our formula assumes all avoided E becomes available water,
so **recoverable E is an upper bound on volume and a lower bound on productivity
gain.**

**Retrieval uncertainty is highest where our signal is.** ETLook's E/T
partitioning over standing water and flooded surfaces is weakly constrained — the
energy balance over a ponded paddy is not the case the model is best calibrated
for. Our entire result rests on the E/T split in the one land surface where that
split is least trustworthy. There is no rebuttal to this. Disclose it.

## 3c. Verified against the real asset — 19 Aug 2026
**This section records the first contact between the method and real WaPOR data.**

Google Earth Engine, WaPOR v3 L2, summer 2024, 18 dekads, central Nile Delta:

| Quantity | Value | Read |
|---|---|---|
| Scale property on the asset | 0.1 | DN × 0.1 = mm/**day**, not mm/dekad |
| Seasonal AETI | 617 mm | Squarely in the expected 450–800 range |
| Seasonal E | 135 mm | — |
| Seasonal T | 484 mm | — |
| **E / AETI** | **0.22** | Non-beneficial share |
| **T / AETI** | **0.78** | Beneficial fraction |

**A trap worth recording.** Because a dekad is about 10 days, multiplying by the
0.1 scale and then by the day count very nearly cancels — so the raw integer
reads as millimetres per dekad whether or not the scale was applied. Both
readings produce a plausible seasonal total. The raw value is therefore a
**useless test on its own**; only the seasonal total distinguishes them. Our
first diagnostic would have passed a 10× error.

**The prize is smaller than the demo assumed.** Demo data implied a beneficial
fraction near 0.63 and E/AETI near 0.35. The real central Delta is more
efficient than that: 0.78 and 0.22. Less non-beneficial evaporation means less
recoverable water, so **every magnitude in this repository will fall when real
rasters replace the placeholders.** The ranking is the claim; the magnitude was
always going to move.

**Two upward biases in that 0.78, both ours.** The sample box excludes the
northern lakes and the desert margins, and the BF > 0.15 open-water filter
removes low-BF pixels by construction. The study-area figure should come in
below 0.78. Do not quote the central-Delta number as a national one.

## 3d. First run on real data — the prior was wrong
> **Superseded in part by §3f.** The figures in this section predate the
> open-water correction and are kept because the reasoning still holds and the
> sequence of corrections is itself the record. For current numbers use §3f.
**19 Aug 2026, WaPOR v3 L2, summer 2024, 18 dekads, 3.57 Mha observed irrigated.**

We built this expecting the northern Delta rice belt to lead, on the reasoning
that ponded paddy evaporates all season. **The data says the opposite.** The rice
belt has the *highest* beneficial fraction in Egypt; Upper Egypt has the lowest.

| System | Irrigated | AETI | E | E/AETI |
|---|---|---|---|---|
| Delta — rice belt | 1.76 Mha | 592 mm | 120 mm | **0.20** |
| Delta — other | 0.61 Mha | 500 mm | 127 mm | 0.26 |
| **Nile Valley** | 1.20 Mha | 684 mm | **186 mm** | **0.27** |

Damietta reaches 0.84 beneficial fraction and Kafr El Sheikh 0.81 — among the
most efficient irrigated landscapes you will measure anywhere. The physical
explanation is straightforward once you stop assuming: a closed rice canopy
**shades** the water surface, so ponding does not imply evaporation. Upper Egypt
is hotter, has higher evaporative demand, and grows wider-row crops that leave
more bare soil exposed for longer.

**Consequences, all of which must propagate to the pitch:**

- The recommendation is now **Aswan, Qena, Sohag, Assiut, Beni Suef, Minya** —
  Upper Egypt, not the Delta.
- The lake-contamination worry is largely moot: the Delta is not the answer, so
  Burullus and Manzala cannot be manufacturing it. **Lake Nasser in Aswan now
  matters instead**, and Aswan is the top-ranked unit at *low* confidence.
- Total recoverable evaporation is **5,120 Mm³/season**, not the 7,722 the
  synthetic placeholders implied.
- The advantage of targeting rose to **+32%**, but the share attributable to
  satellite *detail* fell to **+4.5 points** (see below).

**Independent validation.** Observed irrigated area came to 3.57 Mha against
3.21 Mha of reported cultivated area — an 11% overshoot, which is the right
direction and the right order for a satellite that also sees orchards, canal
banks and reclamation the statistics miss. And E + T + I summed to AETI exactly,
which confirms the scale factor and day-count corrections are right.

**One unit excluded.** GAUL's Luxor polygon is 12 km² — that is the city, not
the governorate — which put a nonsense row second on the ranked list.
`04_rank_and_allocate.py` now drops units below 5,000 ha of observed irrigated
land and prints what it dropped. Port Said goes too, at 1,325 ha.

## 3e. The information-value result got weaker, and we are keeping it
> **Superseded by §3f.** Current figures: **+25.2%** real per-district,
> **+21.5%** per-system average, **0%** spatially flat — so satellite detail is
> worth **3.7 points**. The argument below is unchanged.

**+32.2% with real per-district evaporation. +27.7% knowing only a per-system
average. 0% with evaporation spatially flat.**

So satellite *detail* is worth about **4.5 percentage points**, down from the 8.2
the synthetic data suggested. Most of the value sits in the system-level pattern
— Valley versus Delta versus rice belt — which is a coarse agronomic map, not a
satellite product.

**The honest reading, and it is still a good argument.** WaPOR's value here was
in *discovering* the pattern, not in the marginal targeting once you know it. We
would have spent the budget in the Delta on the strength of a textbook
intuition about ponded rice. The satellite is what told us the intuition was
backwards. The information value of a measurement is largest the first time you
look — and that is worth more than 4.5 points.

## 3f. We contaminated our own result, and caught it
**This is the correction that mattered most.**

Aswan came out first in the national ranking. Checking the pixel distribution
behind that: seasonal E reached **1,834 mm**, with 5,392 pixels above 600 mm.
Cropland cannot evaporate at that rate. Lake Nasser, the Toshka lakes, the Nile
channel, main canals and Delta aquaculture ponds had survived **both** the JRC
surface-water mask and the beneficial-fraction test — GSW's occurrence baseline
misses fluctuating margins and newer water bodies, and a partially vegetated
shoreline pixel can still clear T/AETI > 0.15.

The effect was not subtle. Aswan's mean E was **274 mm against a median of
192 mm** — the mean was being set by contamination, and it had put Aswan top of
the list on that alone.

**Fix:** `MAX_E_MM = 600` in `03_zonal_stats.py`. Every governorate's 99th
percentile of cropland E sits under 400 mm; open water sits above 1,200 mm.
Nothing real lives in between, so the cut is clean and does not bias by
efficiency the way raising the beneficial-fraction threshold would.

**After the fix:** Aswan's E falls 274 → 186 mm, its confidence flag improves
from low to medium, and its lead over Qena essentially disappears. The national
gain falls from +32.2% to **+25.2%**, and recoverable evaporation from 5,120 to
**4,844 Mm³**.

**And the system-level story changed with it.** Before the fix, Upper Egypt
looked clearly worse than the Delta. After it, the evaporated *fraction* is
close to uniform — rice belt 0.210, Nile Valley 0.241, rest of Delta 0.243. The
robust finding is not "Upper Egypt is wasteful". It is:

1. **The rice belt is the most efficient land in Egypt**, not the least —
   Damietta 0.157, Kafr El Sheikh 0.191. A closed canopy shades the ponded water.
2. **The ranking is driven by throughput, not by practice.** Upper Egypt pushes
   660–775 mm through a field against the Delta's 510–640, so a similar
   inefficiency costs more water. Targeting follows the heat.

Both of those are more defensible than what we had before, and neither was
available from the synthetic data.

## 4. The AETI > 200 mm cropland mask
**Confidence: medium-high. Impact: medium.**

In Egypt this works unusually well: no rain, no water outside the irrigated
system, so seasonal AETI is near zero in the desert and several hundred mm on
irrigated land. The threshold sits in a genuine gap in the distribution.

Where it fails: open water. The northern lakes (Burullus, Manzala, Idku, Maryut)
and Lake Qarun in Fayoum evaporate freely all season and clear the threshold
easily, with E/AETI near 1.0. They sit inside our top-ranked governorates, so
unmasked they would *manufacture* the exact result we are pitching.

**Now handled, two ways.** `03_zonal_stats.py` drops any pixel whose beneficial
fraction T/AETI falls below 0.15 — physically impossible for a crop, characteristic
of open water. `pipeline/gee/wapor_export.js` additionally masks JRC Global Surface
Water occurrence > 50% at source. Run both. Until real rasters are loaded, treat
the named top three as provisional.

**A second failure mode, still open.** The mask also excludes water-stressed and
deficit-irrigated cropland — exactly the tail-end fields where poor performance
concentrates, which is what an accountability tool exists to find. And the
confidence metric computes its coefficient of variation over the already-masked
subset, so a mostly-desert governorate gets a *narrower* distribution and
therefore a *higher* confidence score. The confidence flag is currently
anti-correlated with what it claims to measure. Fix before Phase 2.

---

## 5. One intervention per governorate
**Confidence: it is a simplification. Impact: low — but not for the reason we first gave.**

We previously claimed this constraint made the targeted result *conservative*.
It does not: `allocate_uniform` applies the same one-best-measure rule to the
baseline, so the constraint is symmetric and cancels. At a $12M budget it does
not bind at all. Where it does bite is at large budgets, where the targeted run
can exhaust its options and leave money unspent. Corrected here rather than left
standing.

---

## 5b. The baseline is a neutral prior, not observed practice
**Confidence: we have no citation either way. Impact: high — it is the comparator.**

We compare against an area-proportional split. We have **no evidence** that MWRI
actually allocates this way, and Egypt's on-farm modernisation is largely
delivered through irrigation directorates and command areas under donor-financed
mesqa/marwa programmes that already carry targeting criteria. So this is the
defensible *neutral prior* — what you would do knowing only where the cropland is
— and it must be described that way, never as "what happens today."

**And it matters how you phrase it.** Against a literal equal split across twenty
governorates the gain looks far larger than against an area-proportional split.
Quoting the bigger number against the weaker strawman is the single easiest way
to lose credibility with this jury.

## 5c. How much of the result is actually WaPOR?
**This is the question to answer before it is asked.**

`04_rank_and_allocate.py` re-runs the whole allocation with WaPOR progressively
removed, and reports the result in `summary.json["counterfactuals"]`:

| Information available | Gain vs baseline |
|---|---|
| Real per-district evaporation (what WaPOR gives you) | **+23%** |
| Evaporation known only as a per-system average (a textbook) | +15% |
| Evaporation spatially flat (no satellite at all) | **0%** |

Two honest conclusions. With no spatial information, targeting buys you
*nothing* — the entire advantage is spatial, which is a genuine argument for
the satellite. But roughly two thirds of it is recoverable from a coarse
agronomic classification, so the part attributable to satellite *detail* is
about **8 percentage points**, not 23. Say the 8 yourself.

## 6. Governorates as the decision unit
**Confidence: defensible. Impact: medium.**

National budget allocation happens at roughly this level, so it matches the
decision. But it is coarser than IPAT's 20 m and coarser than the command areas a
scheme manager works with, and it hides within-governorate variation — which is
exactly the variation IPAT was built to show. Swapping in irrigation-directorate
boundaries is the single highest-value upgrade to this project.

---

## 7. Demo data
**While the red banner is showing, none of the ET values are real.**

They are drawn from plausible published ranges so the demo does not look absurd,
and shaped so the rice belt has the lowest beneficial fraction — the physical
story the concept rests on. They are still invented. Run steps 02 and 03 before
any number is quoted to anyone.
