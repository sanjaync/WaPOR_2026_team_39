# Team 39 — Miro board fill & 1-minute pitch script

Copy each block onto the matching coloured sticky area. Written to be read aloud.

---

## Board header

| Field | Entry |
|---|---|
| **Team #** | 39 |
| **Case study** | Nile Delta and Valley, Egypt |
| **Tool selected** | **IPAT** — Irrigation assessment tool for Egypt (MWRI, WaPOR v3 Level 3, 20 m, Middle & West Delta, ~1.5 Mha) |
| **Subtheme** | **Governance** (primary) · Dashboarding & Entrepreneurship (secondary) · Communication (cross-cutting) |
| **Governance category** | Category 2 — National: ministries and government agencies |
| **Policy-cycle phase** | Implement, then Monitor |
| **Tool direction** | Accountability — performance assessment and KPIs |

---

## 1. The Core Problem (orange)

- The tools already work. Egypt has **IPAT** running inside MWRI on WaPOR v3 at 20 m — it shows where water productivity is high and low across 1.5 Mha of Delta.
- It stops at the map. A planning officer with a fixed budget still has to decide **where to spend**.
- Today that split is made by cultivated area or political balance across governorates — not by hydrology.
- Nothing in the toolchain says which hectare of subsidy buys the most water back.
- WaPOR's **E / T split — its most decision-relevant output — is essentially unused.**
- The gap is not data and not accuracy. **The output arrives in the wrong units for the decision:** mm/dekad, when the decision is in pounds, hectares and cubic metres.

## 2. The User & Decision (green)

- **User:** planning officer, Ministry of Water Resources and Irrigation.
- **Decision-maker at that scale:** the annual on-farm modernisation budget committee.
- **Constraints:** fixed annual envelope · political pressure to spread evenly across governorates · must justify spending to Ministry of Finance · annual cycle, not dekadal.
- **Specific decision informed:** which governorates receive this season's modernisation budget, in what proportion, with which measure.
- **The moment:** annual budget planning. An existing process, on an existing calendar. No new workflow, no new login, no new institution.
- **The test sentence:** *Because of this, an MWRI planning officer directs this season's budget down a ranked list, instead of splitting it in proportion to cultivated area across every governorate.*

## 3. Action & Impact (red)

- Rank every governorate by **recoverable non-beneficial evaporation** (E × irrigated area × reduction fraction × seasons per year).
- Match each to its cheapest effective measure; compute **USD per m³ of water recovered**.
- Spend the budget **down that list**, cheapest water first.
- **Result at $12M: +25% more water than an area-proportional split** — same money, same measures, different order.
- **We ran the idea on real data and our prior was wrong.** We expected the northern Delta rice belt to be the worst. It is the **best**: Damietta 0.157 and Kafr El Sheikh 0.191 evaporated share, the most efficient irrigated land we measured in Egypt. A closed rice canopy shades the ponded water, so ponding does not imply evaporation.
- **The second surprise:** the wasted *fraction* is similar almost everywhere, around 0.24. What differs is **throughput** — Upper Egypt pushes 660–775 mm through a field against the Delta's 510–640, so the same inefficiency costs more water. Targeting follows the heat, not bad practice.
- **We also caught ourselves contaminating our own result.** Lake Nasser, the Toshka lakes, canals and fish ponds survived both the satellite water mask and our beneficial-fraction test, evaporating 1,300–1,800 mm. In Aswan that was 5,392 pixels, and it had put Aswan top of the national ranking on contamination alone. A physical ceiling on cropland evaporation removed it — and most of Aswan's lead went with it.
- **The self-audit:** flat evaporation → targeting gains **zero**; per-system average → +21.5%; real per-district → +25.2%. Satellite *detail* is worth about **3.7 points**; the rest is the system-level pattern the satellite corrected for us.
- **Equity is priced, not ignored.** Reserving 25% of the budget to spread across all eighteen governorates still funds every one of them and costs only **3.2%** of the water. That is the recommendation a budget committee can actually sign.
- **Monitoring closes the loop:** WaPOR sees funded and unfunded districts next season — a built-in control group. Observed impact, not reported progress.

## 4. Ecosystem & Delivery (blue)

- **Sits downstream of IPAT** — an added layer inside a tool MWRI already runs, not a competitor.
- Output is a **two-page district brief**, the format a ministry memo already uses, exportable in one click.
- Plus a **web dashboard where the budget is a slider**, so the committee explores allocations live in the room rather than receiving a fixed answer.
- **Cost assumptions and the equity floor are editable inputs, not hidden constants.** The committee argues with the model, changes what it disagrees with, and leaves owning the result.
- Runs on **WaPOR Level 2 (100 m), globally available** — no dependency on Level 3 coverage, so the method transfers to any WaPOR country.
- Fully open: Python pipeline + a single self-contained HTML file that works offline.
- **What can't be captured in pixels:** a ranked list that ignores political reality gets ignored in turn. The tool is built to lose an argument gracefully — which is what makes it likely to be used at all.

---

## Summary sticky — the 1-minute video script

*(~155 words, about 58 seconds at a normal pace)*

**Do not include in the recorded pitch:** team names or countries, your team number, **the theme you selected**, **next steps**, or heavy technical detail. 45% of the score is the decision-maker's mandate and the tool's alignment with it — spend the first half of the video there.
>
> Egypt's Ministry of Water Resources and Irrigation has to make a fixed share of the Nile feed a hundred and ten million people. Every year it spends a budget modernising farms, and every year it has to justify that spending.
>
> But nothing tells it where. So the money gets spread by cultivated area, or by political balance.
>
> The ministry already runs a WaPOR tool that shows where water productivity is low. It doesn't say where to spend. We add that one step.
>
> WaPOR can separate water that grew a crop from water that simply evaporated.
>
> We rank every governorate by how much evaporated water is recoverable and what it costs to recover — and hand the committee an ordered spending list. Same budget, a quarter more water.
>
> It also told us we were wrong. We expected the rice Delta to be the worst. It's the most efficient land in the country.
>
> And next season WaPOR sees the districts we funded and the ones we didn't. So for the first time, the ministry can check whether the money worked.

---

## Three things to say before the jury asks

1. **Field-scale is not basin-scale.** Some water an intervention frees up was already returning to a drain and being reused downstream. Suppressing evaporation can also convert it to transpiration and yield rather than to saved water. Recoverable E is an **upper bound**. These figures rank places against each other; they are not a water account.
2. **The ranking is robust, the magnitude is not.** The order of places is driven by observed evaporation, which varies about twofold across the study area. The size of the prize moves with every cost coefficient. We found this by adversarially testing our own model — an earlier version of our claim did not survive it, and we corrected it.
3. **The comparator is a neutral prior, not observed practice.** We have no citation for how MWRI actually splits this budget, and Egypt delivers much of it through irrigation directorates rather than governorates. We compare against area-proportional allocation because that is what you would do knowing only where the cropland is.

**And one we fixed rather than defended:** the northern lakes. Burullus, Manzala, Idku, Maryut and Qarun all sit in our top-ranked governorates and evaporate freely, which would have manufactured our own result. They are now masked twice — by beneficial fraction in the pipeline, and by JRC surface water at source.

Saying these first is the cheapest way to look like the most mature team in the room.
