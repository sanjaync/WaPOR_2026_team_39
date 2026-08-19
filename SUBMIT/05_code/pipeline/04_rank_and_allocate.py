#!/usr/bin/env python3
"""
Step 04 - THE DECISION STEP.

Turns per-governorate evaporation statistics into a ranked spending list.

Input : data/interim/zonal_stats.geojson   (from step 03, or make_demo_data.py)
Output: webmap/data/districts.geojson      (map payload)
        webmap/data/summary.json           (allocation result + assumptions)

The logic, in full
------------------
Recoverable water, per governorate x intervention:

    V_rec [m3] = E_mm x irrigated_ha x 10 x e_reduction

    (1 mm over 1 ha = 10 m3.  E_mm is mean seasonal soil/open-water evaporation:
     water that left the field without passing through a stoma, i.e. without
     growing anything. e_reduction is the fraction of that a given measure avoids.)

Annualised cost:

    C_ann [USD] = usd_per_ha / life_years x irrigated_ha

Unit cost of saved water:

    c = C_ann / V_rec   [USD per m3]

Allocation: sort every (governorate, intervention) option by c ascending and
spend the budget down that list - cheapest water first. This is a greedy
knapsack, which is optimal here because the options are near-continuous
(a governorate can be part-treated).

Baseline for comparison: the same budget spread across governorates in
proportion to irrigated area, which is what actually happens today.

Everything the result depends on is exposed in summary.json["assumptions"] so a
reviewer can see, change and disagree with it.
"""
import json
import sys
from pathlib import Path

import geopandas as gpd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (DATA_INTERIM, DEFAULT_BUDGET_USD, INTERVENTIONS,
                    SEASON_LABEL, WEBMAP_DATA)


def build_options(gdf):
    """Every (governorate, intervention) pair that is physically applicable."""
    options = []
    for _, r in gdf.iterrows():
        for key, iv in INTERVENTIONS.items():
            if r["system"] not in iv["applies_to"]:
                continue
            ha = float(r["irrigated_ha"])
            if ha <= 0 or r["e_mm"] <= 0:
                continue
            # Costs are annualised, so water saved must be annualised too.
            # Laser levelling and drip persist through the winter (shitwi) season;
            # AWD and mulching are single-season measures. Counting one season for
            # all of them silently favoured the single-season measures.
            seasons = iv.get("seasons_per_year", 1)
            v_rec = r["e_mm"] * ha * 10.0 * iv["e_reduction"] * seasons   # m3/year
            c_ann = iv["usd_per_ha"] / iv["life_years"] * ha         # USD/year
            options.append({
                "gov": r["gov"],
                "system": r["system"],
                "intervention": key,
                "intervention_label": iv["label"],
                "irrigated_ha": ha,
                "e_mm": float(r["e_mm"]),
                "recoverable_m3": v_rec,
                "cost_usd": c_ann,
                "usd_per_m3": c_ann / v_rec if v_rec > 0 else float("inf"),
                "confidence": r["confidence"],
            })
    return sorted(options, key=lambda o: o["usd_per_m3"])


def allocate_targeted(options, budget, equity_floor=0.0, gdf=None):
    """Cheapest water first, with an optional equity floor.

    equity_floor is the share of the budget reserved to be spread across ALL
    districts in proportion to irrigated area, before the remainder is targeted.

    Why it exists: a pure cheapest-first rule sends 100% of the money to three
    districts out of twenty, and at a small budget to exactly one. No ministry
    with an equity mandate will sign that, so a recommendation that ignores it
    is a recommendation that gets ignored. The floor makes the political
    constraint explicit and, more usefully, prices it - see cost_of_equity in
    the summary. That number ("an equity floor of 30% costs 9% of the water")
    is more useful to a committee than either extreme on its own.
    """
    best_of = {}
    for o in options:
        best_of.setdefault(o["gov"], o)

    funded = {}          # gov -> usd

    # --- reserved share, spread by irrigated area across every district ---
    reserved = budget * equity_floor
    if reserved > 0 and gdf is not None:
        total_ha = float(gdf["irrigated_ha"].sum())
        if total_ha > 0:
            for _, r in gdf.iterrows():
                o = best_of.get(r["gov"])
                if o is None:
                    continue
                share = reserved * float(r["irrigated_ha"]) / total_ha
                funded[r["gov"]] = min(share, o["cost_usd"])

    # --- remainder, cheapest water first ---
    remaining = budget - sum(funded.values())
    for o in options:
        if remaining <= 0:
            break
        gov = o["gov"]
        if best_of[gov] is not o:        # one measure per district
            continue
        headroom = o["cost_usd"] - funded.get(gov, 0.0)
        if headroom <= 0:
            continue
        take = min(headroom, remaining)
        funded[gov] = funded.get(gov, 0.0) + take
        remaining -= take

    picks, spent, saved = [], 0.0, 0.0
    for gov, usd in sorted(funded.items(), key=lambda kv: best_of[kv[0]]["usd_per_m3"]):
        if usd <= 0:
            continue
        o = best_of[gov]
        frac = usd / o["cost_usd"]
        spent += usd
        saved += o["recoverable_m3"] * frac
        picks.append({**o,
                      "funded_usd": usd,
                      "funded_fraction": frac,
                      "water_saved_m3": o["recoverable_m3"] * frac,
                      "ha_treated": o["irrigated_ha"] * frac})
    return picks, spent, saved


def allocate_uniform(options, gdf, budget):
    """Area-proportional baseline.

    NOT a documented description of MWRI practice - we have no citation for how
    the modernisation budget is actually split, and Egypt's on-farm programmes
    are largely delivered through irrigation directorates rather than
    governorates. This is the defensible NEUTRAL PRIOR: what you would do
    knowing only where the cropland is. Call it that, not "what happens today".
    """
    total_ha = float(gdf["irrigated_ha"].sum())
    if total_ha <= 0:
        return 0.0, 0.0
    spent = saved = 0.0
    for _, r in gdf.iterrows():
        share = budget * float(r["irrigated_ha"]) / total_ha
        local = [o for o in options if o["gov"] == r["gov"]]
        if not local or share <= 0:
            continue
        best = min(local, key=lambda o: o["usd_per_m3"])
        take = min(share, best["cost_usd"])
        spent += take
        saved += best["recoverable_m3"] * (take / best["cost_usd"])
    return spent, saved


def counterfactual_gains(gdf, budget):
    """How much of the advantage is actually attributable to WaPOR?

    The honest question a juror will ask: could you have got most of this from a
    textbook? We answer it ourselves by re-running the allocation with WaPOR
    progressively removed:

      full        real per-district E                     (what WaPOR gives you)
      by_system   E replaced by its per-system mean       (an agronomy textbook)
      flat        E replaced by one national mean         (no spatial info at all)

    The gap between `full` and `by_system` is the part only a satellite could
    have told you. Reporting it is the difference between a claim and a finding.
    """
    import copy
    out = {}
    for label, mode in (("full", None), ("by_system", "system"), ("flat", "flat")):
        g = gdf.copy()
        if mode == "system":
            g["e_mm"] = g.groupby("system")["e_mm"].transform("mean")
        elif mode == "flat":
            g["e_mm"] = g["e_mm"].mean()
        opts = build_options(g)
        _, sp, sv = allocate_targeted(opts, budget, gdf=g)
        usp, usv = allocate_uniform(opts, g, budget)
        # spend-neutral: compare USD per m3, not raw volume, because the
        # area-proportional baseline can underspend at large budgets.
        out[label] = {
            "targeted_mcm": round(sv / 1e6, 1),
            "baseline_mcm": round(usv / 1e6, 1),
            "targeted_usd_per_m3": round(sp / sv, 4) if sv else None,
            "baseline_usd_per_m3": round(usp / usv, 4) if usv else None,
            "gain_volume_pct": round((sv / usv - 1) * 100, 1) if usv else 0.0,
            "gain_unitcost_pct": round((usp / usv) / (sp / sv) * 100 - 100, 1)
                                 if (sv and usv and sp and usp) else 0.0,
        }
    return out


def main(budget: float = DEFAULT_BUDGET_USD) -> None:
    gdf = gpd.read_file(DATA_INTERIM / "zonal_stats.geojson")
    meta = json.loads((DATA_INTERIM / "zonal_meta.json").read_text())

    gdf["beneficial_fraction"] = (gdf["t_mm"] / gdf["aeti_mm"]).round(3)
    gdf["nonbeneficial_m3"] = (gdf["e_mm"] * gdf["irrigated_ha"] * 10.0).round(0)
    gdf["nonbeneficial_mcm"] = (gdf["nonbeneficial_m3"] / 1e6).round(1)

    options = build_options(gdf)
    picks, spent, saved = allocate_targeted(options, budget, gdf=gdf)
    u_spent, u_saved = allocate_uniform(options, gdf, budget)

    # Price the political constraint at a few equity floors
    equity = []
    for floor in (0.0, 0.25, 0.50, 0.75, 1.0):
        pk, sp, sv = allocate_targeted(options, budget, equity_floor=floor, gdf=gdf)
        equity.append({
            "equity_floor": floor,
            "districts_funded": len(pk),
            "water_saved_mcm": round(sv / 1e6, 1),
            "usd_per_m3": round(sp / sv, 4) if sv else None,
            "water_lost_vs_pure_targeting_pct":
                round((1 - sv / saved) * 100, 1) if saved else 0.0,
        })

    cf = counterfactual_gains(gdf, budget)

    # Best available option per governorate -> what the map shows
    best_by_gov, rank_by_gov = {}, {}
    for o in options:
        if o["gov"] not in best_by_gov:
            best_by_gov[o["gov"]] = o
    for i, (gov, _) in enumerate(
            sorted(best_by_gov.items(), key=lambda kv: kv[1]["usd_per_m3"]), 1):
        rank_by_gov[gov] = i

    funded = {p["gov"]: p for p in picks}
    gdf["rank"] = gdf["gov"].map(rank_by_gov).fillna(999).astype(int)
    gdf["best_intervention"] = gdf["gov"].map(
        lambda g: best_by_gov.get(g, {}).get("intervention_label", "-"))
    gdf["usd_per_m3"] = gdf["gov"].map(
        lambda g: round(best_by_gov.get(g, {}).get("usd_per_m3", 0), 4))
    gdf["recoverable_mcm"] = gdf["gov"].map(
        lambda g: round(best_by_gov.get(g, {}).get("recoverable_m3", 0) / 1e6, 2))
    gdf["funded_usd"] = gdf["gov"].map(
        lambda g: round(funded.get(g, {}).get("funded_usd", 0), 0))
    gdf["water_saved_mcm"] = gdf["gov"].map(
        lambda g: round(funded.get(g, {}).get("water_saved_m3", 0) / 1e6, 2))

    WEBMAP_DATA.mkdir(parents=True, exist_ok=True)
    gdf.to_file(WEBMAP_DATA / "districts.geojson", driver="GeoJSON")

    gain = (saved / u_saved - 1) * 100 if u_saved > 0 else 0.0
    summary = {
        "data_status": meta["data_status"],
        "meta": meta,
        "season_label": SEASON_LABEL,
        "budget_usd": budget,
        "targeted": {
            "spent_usd": round(spent),
            "water_saved_mcm": round(saved / 1e6, 1),
            "governorates_funded": len(picks),
            "usd_per_m3": round(spent / saved, 4) if saved else None,
        },
        "uniform_baseline": {
            "spent_usd": round(u_spent),
            "water_saved_mcm": round(u_saved / 1e6, 1),
            "usd_per_m3": round(u_spent / u_saved, 4) if u_saved else None,
        },
        "gain_percent": round(gain, 1),
        "gain_unitcost_percent": round(
            (u_spent / u_saved) / (spent / saved) * 100 - 100, 1)
            if (saved and u_saved and spent and u_spent) else 0.0,
        "counterfactuals": cf,
        "information_value_note": (
            "gain_percent compares targeted allocation against an "
            "AREA-PROPORTIONAL baseline, which is a neutral prior, not "
            "documented ministry practice. counterfactuals['by_system'] shows "
            "what the same method achieves with E known only as a per-system "
            "average - i.e. without a satellite. The difference between 'full' "
            "and 'by_system' is the part attributable to WaPOR."),
        "equity_curve": equity,
        "total_nonbeneficial_mcm": round(float(gdf["nonbeneficial_mcm"].sum()), 1),
        "ranked_options": [
            {k: (round(v, 4) if isinstance(v, float) else v)
             for k, v in o.items()} for o in options[:60]
        ],
        "allocation": [
            {k: (round(v, 2) if isinstance(v, float) else v)
             for k, v in p.items()} for p in picks
        ],
        "assumptions": {
            "interventions": INTERVENTIONS,
            "note": ("Intervention costs and evaporation-reduction fractions are "
                     "literature-order ESTIMATES, not measurements. They are "
                     "editable in the web map. Conclusions are sensitive to them "
                     "and should be presented as such."),
        },
    }
    (WEBMAP_DATA / "summary.json").write_text(json.dumps(summary, indent=2))

    banner = ("  !! DEMO DATA !!" if meta["data_status"] == "DEMO"
              else "  WaPOR v3 data")
    print(banner)
    print(f"\n  Non-beneficial evaporation across the study area: "
          f"{summary['total_nonbeneficial_mcm']:,.0f} Mm3 per season")
    print(f"\n  Budget: ${budget:,.0f}")
    print(f"    targeted : {summary['targeted']['water_saved_mcm']:>7.1f} Mm3  "
          f"(${summary['targeted']['usd_per_m3']:.3f}/m3, "
          f"{len(picks)} governorates)")
    print(f"    uniform  : {summary['uniform_baseline']['water_saved_mcm']:>7.1f} Mm3  "
          f"(${summary['uniform_baseline']['usd_per_m3']:.3f}/m3)")
    print(f"    ---> {gain:+.1f}% more water (volume), "
          f"{summary['gain_unitcost_percent']:+.1f}% on unit cost (spend-neutral)")
    print(f"\n  How much of that is WaPOR?  (same method, less information)")
    for k, lab in (("full", "real per-district E   "),
                   ("by_system", "per-system mean E     "),
                   ("flat", "one national mean E   ")):
        print(f"    {lab} gain {cf[k]['gain_volume_pct']:+6.1f}%   "
              f"${cf[k]['targeted_usd_per_m3']:.3f}/m3")
    print(f"    ---> attributable to satellite detail: "
          f"{cf['full']['gain_volume_pct'] - cf['by_system']['gain_volume_pct']:+.1f} "
          f"percentage points")
    print(f"\n  What an equity floor costs")
    print(f"    {'floor':>6}{'districts':>11}{'Mm3':>9}{'water lost':>12}")
    for e in equity:
        print(f"    {e['equity_floor']*100:5.0f}%{e['districts_funded']:>11}"
              f"{e['water_saved_mcm']:>9.1f}{e['water_lost_vs_pure_targeting_pct']:>11.1f}%")
    print(f"\n  Top of the spending list:")
    print(f"    {'#':<3}{'governorate':<16}{'intervention':<32}"
          f"{'USD/m3':>9}{'Mm3':>8}")
    for i, p in enumerate(picks[:8], 1):
        print(f"    {i:<3}{p['gov']:<16}{p['intervention_label']:<32}"
              f"{p['usd_per_m3']:>9.3f}{p['water_saved_m3']/1e6:>8.1f}")
    print(f"\n  wrote {WEBMAP_DATA/'districts.geojson'}")
    print(f"  wrote {WEBMAP_DATA/'summary.json'}")


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BUDGET_USD)
