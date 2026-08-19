# Team 39 — Idea Shortlist & Miro Fill

WaPOR Hackathon 2026 · "From tools to decisions" · prepared 19 Aug 2026

Structured to drop straight onto your board: **Core Problem → User & Decision →
Action & Impact → Ecosystem & Delivery → Summary**. Two blanks at the top of your
board still need filling — **Case study (region)** and **Tool selected** — so
those get their own sections.

---

## 1. The one insight to build on

The theme is *From tools to decisions*, and that is a deliberate correction. The
2022 and 2023 editions produced tools. FAO's applications catalogue now lists 20+
working ones: IPADT in Jordan, IMISET in Ethiopia, IPON in Mali, the Sudan and
Pakistan drought monitors, water-use tools for Tunisia and Algeria, the IREY app,
Digital Earth Africa. **The data is fine. The tools work. Almost nothing changes.**

So your pitch is not "here is a tool." It is:

> Tool **X** already produces output **Y**. User **Z** still can't act on it because
> of barrier **B**. Our layer converts **Y** into decision **D**, delivered through
> **C**, inside a process that already exists.

**Test any idea with this sentence.** If you can't fill all four blanks, it's a
visualisation, not a decision:

*"Because of this, **[named role]** will do **[specific action]** on **[specific
date/trigger]** instead of **[what they do now]**."*

### Six real reasons WaPOR outputs die before becoming decisions
Pick which one you're attacking — most teams will only see #1.

| # | Barrier | What it looks like on the ground |
|---|---------|----------------------------------|
| 1 | **Format** | Output is mm/dekad. The decision is in canal-days, feddans, or EGP |
| 2 | **Trust** | The gauge says something else. No error bars. No local validation |
| 3 | **Timing** | Dekadal data with lag vs. weekly gate orders and annual budget cycles |
| 4 | **No counterfactual** | "Your WP is 0.8 kg/m³." Compared to whom? Changed how? |
| 5 | **Attention** | Nobody logs into a portal. Pull fails; push works |
| 6 | **Ownership** | The number lands in nobody's inbox and nobody is accountable |

---

## 2. Burned ground — do not pitch these

**2023 finalists:** SenBio (winner — biomass climate-sensitivity DSS), WaPOR.AI
(runner-up — AI forecast of water use and yield one month ahead), WaPLUGIN+ (QGIS
validation), SoWaA (bidirectional soil-water budget with farmer input), Growwise
(crop choice for peri-urban farmers).
**2022 winner:** SMS irrigation/fertiliser advisory for Sudanese farmers.

**Therefore avoid:** an AI/ML forecasting layer on WaPOR (two of five 2023 finalists
did this — expect a crowd again), a crop recommendation app, and a generic farmer
SMS advisory. The jury has seen all three win already.

---

## 3. Filling the two blanks on your board

### Case study — pick this in the first meeting
Your roster is heavily **Nile basin**: Amal, Mohamed and Tamer (Egypt), Amare
(Ethiopia), Austin (Uganda). That is a real asset — three teams out of forty will
have members who can say "I have stood in this irrigation district."

| Option | Why | Watch out |
|--------|-----|-----------|
| **Nile Delta / Middle Egypt irrigation district** ★ | 3 teammates with local knowledge; extreme scarcity per capita; strong institutions (MWRI) that actually make allocation decisions; well-documented | Check WaPOR L3 20m coverage before going field-level |
| **Awash basin, Ethiopia** | Amare's knowledge; IMISET already exists there so you can genuinely build *on a tool*; classic head/tail equity conflict | Less data-rich |
| **Uganda / equatorial Nile** | Austin's knowledge; underserved | Rainfed-dominant, so irrigation framing is weaker |

**Recommendation: Egypt.** Depth of local knowledge on the team beats novelty of
region, and a jury can tell the difference within ten seconds of the pitch.

### Tool selected
The board asks which *particular* tool you chose. Options, in order of how well
they set up a "tools → decisions" story:

1. **WaPORIPA** (open protocol on GitHub, `wateraccounting/WaPORIPA`) — standardised
   irrigation performance assessment on WaPOR v3. Outputs uniformity, equity,
   adequacy, beneficial fraction, relative water deficit, productivity gap.
   *Best pick:* real, open, works anywhere, and its outputs are exactly the kind of
   correct-but-unusable indicators your pitch is about.
2. **IPADT (Jordan)** — irrigation performance and productivity gaps. Great if you
   want to argue "this exists in Jordan, it should drive decisions in Egypt."
3. **IMISET (Ethiopia)** — seasonal water consumption for scheme management. Pick
   this if you choose Awash.
4. **WaPOR portal itself** (wapor.apps.fao.org) — safest, least distinctive.

**Recommendation: WaPORIPA + the WaPOR v3 portal as its data source.**

---

## 4. Shortlist — 8 ideas, ranked

Scored 1–5. *Decision* = a real decision actually changes. *Feasible* = credible
demo + 1-min video in the time you have. *Diff.* = unlike past winners and unlike
what 40 other participants will pitch.

| # | Idea | Primary user | Decision | Feasible | Diff. | Total |
|---|------|--------------|:--------:|:--------:|:-----:|:-----:|
| 1 | **Same Budget, More Water** — evaporation hotspot targeting | Policymaker | 5 | 5 | 5 | **15** |
| 2 | **Water Balance** — seasonal budget as a bank account | Farmer / scheme | 5 | 4 | 4 | **13** |
| 3 | **Go / No-Go** — confidence layer, "when NOT to act" | All three | 4 | 4 | 5 | **13** |
| 4 | **Visit List** — extension agent prioritiser | Institution | 4 | 5 | 4 | **13** |
| 5 | **Equity Pack** — evidence for the WUA meeting | Local governance | 4 | 4 | 4 | **12** |
| 6 | **Report Card** — peer benchmark nudge | Farmer | 5 | 4 | 3 | **12** |
| 7 | **One-Button Brief** — auto cabinet memo | Policymaker | 4 | 5 | 3 | **12** |
| 8 | **Auto-Payout** — parametric insurance trigger | Farmer via finance | 5 | 2 | 4 | **11** |

---

## 5. Top concept, written as your board

### ★ "Same Budget, More Water" — targeting scarce money at recoverable water

WaPOR is one of very few global products that reports **E (evaporation), T
(transpiration) and I (interception) as separate layers**. Almost nobody uses that
split. A high **E/AETI ratio is water leaving the field without growing anything** —
and unlike most water losses, it is recoverable with *cheap* interventions:
mulching, drip retrofit, night irrigation, canal lining, bed planting.

Convert that into a **ranked investment list**. For each district: non-beneficial
evaporation in Mm³/season, the intervention that addresses it, cost per m³ saved,
and the resulting budget split. A ministry with a fixed subsidy budget receives an
ordered spending list, not a map.

**Sticky-note text for each Miro column:**

**1. Core Problem** *(orange)*
- WaPOR tools report ET correctly, but ministries still allocate modernisation
  budgets evenly or politically
- No tool says *where a euro of subsidy saves the most water*
- The E/T split — WaPOR's most distinctive output — is essentially unused
- Result: scarce money spread thin, water savings unmeasured, no accountability

**2. User & Decision** *(green)*
- **User:** planning officer, Ministry of Water Resources & Irrigation (Egypt)
- **Decision-maker at that scale:** the annual on-farm modernisation / subsidy
  allocation committee
- **Constraints shaping their choice:** fixed annual budget, political pressure to
  spread evenly across governorates, must justify spending to Ministry of Finance,
  works on an annual cycle not a dekadal one
- **Specific decision informed:** which districts receive this season's mulching
  and drip-retrofit budget, and in what proportion

**3. Action & Impact** *(red)*
- Rank all districts by recoverable non-beneficial evaporation (E/AETI × area)
- Match each to the cheapest effective intervention; compute cost per m³ saved
- Reallocate budget top-down that list instead of uniformly
- **Measurable improvement:** water saved per unit spent vs. the uniform-allocation
  baseline — computable directly from WaPOR, and re-measurable next season with the
  same data, which closes the accountability loop

**4. Ecosystem & Delivery** *(blue)*
- Delivered as a **2-page district brief** (the format a cabinet memo already uses),
  plus a layer in the national portal they already open
- Fits the **existing annual planning cycle** — no new process, no new login
- Built on **WaPORIPA + WaPOR v3 L1/L2**, globally available, no dependency on
  L3 20m coverage
- Refinement needed: local intervention cost figures, and a validation step against
  ministry field data

**Summary sticky (your 1-min video script, ~150 words):**
> Egypt gets 55 billion cubic metres of Nile water a year and has to grow food for
> 110 million people with it. Every year the ministry spends a fixed budget on
> on-farm modernisation — and spreads it evenly, because nothing tells them where it
> would work best. WaPOR already knows. It separates water that grows crops from
> water that just evaporates off wet soil, at 100 metres, every ten days. Nobody uses
> that split. We rank every district by how much evaporated water is recoverable and
> what it costs to recover it — and hand the ministry an ordered spending list
> instead of a map. Same budget, more water. And because WaPOR sees the same district
> next season, for the first time they can check whether the money worked.

**The weak link the jury will probe:** intervention cost-effectiveness figures are
literature estimates, not measurements. **Say so first, out loud, and make them
user-editable inputs.** Juries reward visible honesty about uncertainty far more
than they reward fake precision — and it is the cheapest way to look like the most
mature team in the room.

---

## 6. The other seven, in brief

**2. Water Balance.** Give every plot or scheme a seasonal volumetric budget from
crop water requirement, then track WaPOR-observed consumption against it like a bank
balance: *"62% of your season's water used, 45% of the season gone."* The metaphor is
the innovation — no training needed, fits on SMS or a noticeboard.
*Decision:* farmer shortens the next turn; manager rations in week 6 instead of
running the tail-end dry in week 14.
*Weak link:* ET ≠ abstraction. State that you budget **consumption**, or an expert
will open with it.

**3. Go / No-Go.** Every tool says what the data shows; none says how much to believe
it *here, right now*. Grade each area on cloud frequency, L1/L2/L3 agreement,
land-cover confusion, distance to validation — output plain language: *act on it* /
*check the field first* / *don't use this pixel*. Trust is the top adoption blocker
and this is the only idea that attacks it directly. It also **composes** — it can
wrap any other concept, which makes it a good merge card.
*Weak link:* must output an instruction, not a QA map.

**4. Visit List.** Extension services are limited by **agent-days**, not data. Rank
which villages an agent visits *this week* from WaPOR anomalies, and generate the
route. Reframes satellite data as a logistics problem. No farmer needs a phone; the
institution already exists and has a budget.

**5. Equity Pack.** Head-end vs. tail-end conflict is the oldest problem in
irrigation. ET distribution along a canal is **neutral third-party evidence** of who
actually gets water. Package it as a printed A3 map + an agreed reallocation rule for
the WUA's monthly meeting. The decision moment is a *meeting*, not a login — the most
realistic last-mile story on this list.

**6. Report Card.** Percentile against neighbours growing the same crop in the same
scheme, one page, with the gap in kg and in currency. This is the OPOWER
home-energy-report effect — one of the best-evidenced behaviour-change results
anywhere — barely tried in irrigation. *Weak link:* tail-enders get less water and
would be blamed for it. Compare **within hydraulic position**, and have that answer
ready.

**7. One-Button Brief.** Auto-generate the 2-page memo a policymaker actually needs.
High real value, low technical wow. **Use it as the output format of #1, not as your
whole pitch.**

**8. Auto-Payout.** WaPOR biomass anomaly as the index for automatic smallholder
insurance payouts — the action is a bank transfer, no human in the loop. Elegant, but
basis risk and insurance regulation are real and a week is not enough. Pitch only if
someone has agri-insurance experience.

---

## 7. Recommendation

**Lead with #1, deliver it in #7's brief format, add #3's confidence grading as your
credibility layer.** That combination:

- uses a WaPOR capability (separate E / T) that most teams will overlook
- produces a decision with a currency sign on it, at the scale where budgets move
- has an explicit honesty story about uncertainty
- runs on globally available L1/L2 data, so no dependency on L3 coverage
- maps cleanly onto all four Miro columns without forcing

**Fallback if the team leans field-level rather than policy-level:** #2 + #5 — the
water balance as the number, the WUA meeting as the delivery moment.

---

## 8. Before your next team call

1. **Lock the case study in the first meeting.** Generic global pitches lose to
   specific ones every time. Egypt is the recommendation.
2. **Lock the tool.** WaPORIPA is the recommendation.
3. **Find one real user.** One email to an actual MWRI planner or extension officer,
   quoted in the pitch, is worth more than any modelling. Amal, Mohamed and Tamer are
   your best route to that — this is the single highest-leverage thing the team can
   do this week.
4. **Decide what you'll demo.** A clickable mock of the *output* beats a working
   pipeline with no output. The jury is judging the decision, not the code.
5. **Use dot voting on the board deliberately.** Nine people will generate forty
   stickies. Put the four barriers table above the voting area so people vote on
   *which barrier to attack*, not on which idea sounds coolest.

---

## Sources

- FAO WaPOR applications catalogue — https://www.fao.org/in-action/remote-sensing-for-water-productivity/applications-catalogue
- WaPOR v3 layers in Google Earth Engine (AETI, E, T, I, NPP, RET; L1 300 m, L2 100 m, dekadal) — https://www.fao.org/in-action/remote-sensing-for-water-productivity/news-and-events/news/news-detail/wapor-v3-data-now-available-on-the-google-earth-engine-data-catalogue/en
- WaPOR v3 global launch — https://www.fao.org/in-action/remote-sensing-for-water-productivity/news-and-events/news/news-detail/wapor-goes-global--version-3.0-was-launched-during-the-rome-water-dialogue---check-all-the-updates/en
- 2023 hackathon finalists — https://www.un-ihe.org/news/wapor-hackathon-2023-bridging-gap-between-data-and-decision-making
- 2023 winner SenBio — https://www.fao.org/in-action/remote-sensing-for-water-productivity/news-and-events/news/news-detail/senbio-is-the-2023-wapor-hackathon-winner/en
- 2022 winner (Sudan SMS advisory) — https://www.fao.org/hih-geospatial-platform/news/detail/wapor-hackathon-closes-with-a-winner-proposal-for-an-advisory-service-for-sudanese-farmers/en
- WaterPIP tools — https://waterpip.un-ihe.org/tools-and-publications
- WaPORIPA / WAPORACT / WaPORMOOC code — https://github.com/wateraccounting
- WaPOR portal — https://wapor.apps.fao.org/
