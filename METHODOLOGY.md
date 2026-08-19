# 🔬 The Methodology: How WaPOR Satellite Data Solves Egypt's Budget Problem

To solve Egypt's budget problem, the team uses a clever method that relies on **FAO's WaPOR (Water Productivity through Open access of Remotely sensed data) database**. This free satellite system measures water use from space.

The team's method is divided into **three key parts**: cleaning up the satellite data, running a simple three-line mathematical calculation, and then sorting the results to get the most "bang for the buck".

---

## Step 1️⃣: Cleaning and Isolating the "Wasted" Water Data

Before doing any math, the team has to clean the raw satellite data so they are only looking at actual, irrigated farm crops.

### 📊 Summing Up the Season

The team takes the satellite's 10-day reports (called **"dekads"**) and adds up all **18 periods from May 1 to October 31** (the summer growing season). They apply a mathematical correction to turn raw satellite rates into actual, physical millimeters of water used over the whole season.

```
Seasonal Water Use = Sum of all dekads × Calibration factor
                   = 18 dekads × (correction for physical units)
                   = Total millimeters of water for the entire season
```

### 🏜️ Filtering Out the Desert

Since Egypt is mostly desert, they automatically **ignore any land** where the seasonal water use is below **200 mm**, leaving only irrigated farm fields.

| Land Type | Seasonal Water Use | Action |
|-----------|-------------------|--------|
| Desert/Barren Land | < 200 mm | ❌ Filtered out |
| Irrigated Farmland | ≥ 200 mm | ✅ Kept for analysis |

### 💧 Removing Open Water (The "Aswan Correction")

This is a **critical step**. Open bodies of water (like Lake Nasser, canals, or fish ponds) evaporate massive amounts of water and can trick the satellite into thinking they are highly wasteful farm fields.

To prevent this, the team filters out any pixels that meet any of these criteria:

| Criterion | Threshold | Why It Matters |
|-----------|-----------|----------------|
| Open water coverage | > 50% of the time | Lakes and canals evaporate differently than crops |
| Plant growth | Virtually none | Open water has no vegetation |
| Seasonal evaporation rate | > 600 mm | Exceeds what any farm crop would use |

Once these filters are applied, the team has **clean, high-quality data** showing:
- **How much water is evaporating (wasted)** — denoted as $E_i$ for district $i$
- **How much land is being farmed** — denoted as $A_i$ for district $i$

---

## Step 2️⃣: The Three-Line Math Model

With clean data in hand, the team runs a simple, transparent **three-line calculation** for every region ($i$) and every potential modernizing method ($j$, like soil leveling or better rice watering):

### 📐 Line 1: Calculate Recoverable Water ($V$)

$$V = E_i \times A_i \times 10 \times r_j \times n_{\text{seasons}}$$

**What this means:**
- $E_i$ = Evaporation rate in the district (millimeters per season)
- $A_i$ = Irrigated area in the district (hectares)
- $10$ = Conversion factor (millimeters to cubic meters)
- $r_j$ = Reduction rate for method $j$ (e.g., 20% reduction = 0.20)
- $n_{\text{seasons}}$ = Number of growing seasons per year

**In plain English:** This calculates exactly how many **cubic meters of water can actually be saved per year** by deploying a specific measure on that land.

### 💰 Line 2: Calculate the Annualized Cost ($C$)

$$C = \left(\frac{\text{Upfront Cost per Hectare}}{\text{Service Life in Years}}\right) \times A_i$$

**What this means:**
- Upfront Cost per Hectare = Total installation cost per hectare
- Service Life in Years = How many years the equipment lasts
- $A_i$ = Irrigated area in the district (hectares)

**In plain English:** This determines the **actual cost per year** to install and maintain the irrigation equipment over its entire lifetime. Instead of just looking at upfront costs, this spreads them out fairly across all the years the equipment will work.

**Example:**
```
If soil leveling costs $500/hectare and lasts 10 years:
  Annual cost = ($500 / 10 years) × Area
             = $50/hectare/year × Area
```

### 🎯 Line 3: Calculate the Cost of Saved Water ($\kappa$)

$$\kappa = \frac{C}{V} = \frac{\text{Annualized Cost}}{\text{Recoverable Water}}$$

**What this means:**
- $C$ = Annual cost to run the intervention (USD per year)
- $V$ = Water recovered per year (cubic meters)

**In plain English:** This gives the final, critical metric: **the exact price in USD per cubic meter of water saved** ($USD/m^3$).

**Example:**
```
If an intervention costs $50,000/year and saves 5,000,000 m³/year:
  κ = $50,000 / 5,000,000 m³
    = $0.01 per cubic meter saved
```

---

## Step 3️⃣: Spending Down the List ("The Greedy Solution")

Once every district has a price tag for its saved water, the team simply **sorts the list from the cheapest saved water to the most expensive**.

### 📊 The Ranking

```
Rank  |  District        |  κ (Cost/m³)  |  Water Saved (Mm³)  |  Cost
------|------------------|----------------|---------------------|----------
  1   |  District A      |  $0.008        |  12.5               |  $100k
  2   |  District B      |  $0.012        |  8.3                |  $100k
  3   |  District C      |  $0.018        |  5.6                |  $100k
  4   |  District D      |  $0.025        |  4.0                |  $100k
  5   |  District E      |  $0.035        |  2.9                |  $100k
 ... |  ...              |  ...           |  ...                |  ...
  18  |  District R      |  $0.082        |  1.2                |  $100k
```

### 💡 The Strategy

The budget committee then starts **spending their money from the top of the list** (the cheapest water) and works their way down until the budget runs out.

```
Total Budget: $500,000

Step 1: Fund District A ($100k) → Save 12.5 Mm³ at $0.008/m³
Step 2: Fund District B ($100k) → Save 8.3 Mm³ at $0.012/m³
Step 3: Fund District C ($100k) → Save 5.6 Mm³ at $0.018/m³
Step 4: Fund District D ($100k) → Save 4.0 Mm³ at $0.025/m³
Step 5: Fund District E ($100k) → Save 2.9 Mm³ at $0.035/m³
─────────────────────────────────────────────────────────
TOTAL INVESTED: $500,000  |  TOTAL WATER SAVED: 33.3 Mm³
```

### ✅ Why This Works: Guaranteed Optimality

Because districts can be **partially upgraded** (if you have leftover budget, you can fund part of the next-cheapest option), this "greedy" mathematical approach is **guaranteed to rescue the absolute maximum amount of water possible** for any given budget size.

**Mathematical guarantee:** If you always pick the cheapest option next, you can never do better than the solution you get by following the list.

---

## 🌍 Real-World Interventions: What $j$ Actually Means

The model doesn't care *what* the intervention is—it just needs a **cost per hectare** and a **water-saving percentage**. But here are some real examples:

| Intervention | Cost/Hectare | Service Life | Water Saved | Best Used In |
|--------------|--------------|--------------|-------------|--------------|
| **Laser Land Leveling** | $100–200 | 10 years | 15–20% of evaporation | Flood-irrigated areas with uneven terrain |
| **Drip Irrigation** | $2,000–3,000 | 10 years | 30–40% of evaporation | Vegetables, orchards |
| **Alternate Wetting & Drying (Rice)** | $50–100 | 1 year | 20–25% of evaporation | Rice fields (labor-intensive but cheap) |
| **Canal Lining** | $5,000–10,000 | 20 years | 10–15% of conveyance losses | Major irrigation channels |
| **Improved Scheduling** | $10–20 | 1 year | 5–10% of evaporation | Any cropped area (requires monitoring) |

---

## ⚖️ Introducing Real-World Politics: The Equity Floor

The "greedy" algorithm is mathematically perfect—but it has a political problem: it would spend **all the budget in just 7 of Egypt's 18 provinces**, leaving the other 11 with nothing.

In the real world, no government can do that without sparking outrage. So the team built in an **"equity floor" slider**:

### How It Works

```
If Equity Floor = 25%:
  ├─ Set aside 25% of budget ($125k of $500k)
  │  └─ Distribute proportionally to all 18 provinces
  │     (based on population, farm size, or political boundaries)
  │
  └─ Spend remaining 75% of budget ($375k)
     └─ Use the greedy algorithm on the leftovers
```

### The Trade-off

| Equity Floor | Water Saved | Provinces Funded |
|--------------|-------------|------------------|
| 0% (Pure Math) | 33.3 Mm³ (100%) | 7 provinces |
| 25% (Balanced) | 32.2 Mm³ (96.7%) | All 18 provinces |
| 50% (Generous) | 30.1 Mm³ (90.4%) | All 18 provinces |

**The insight:** By setting aside just 25% for fairness, the committee can fund all 18 provinces while **only losing 3.3% of maximum water savings**. This lets the committee **balance math with real-world politics** right in the meeting room.

---

## ✅ Verification: Proving It Works Next Season

Because this system uses satellites, the government doesn't have to just trust reports on paper.

### The Verification Process

```
Year 1: Deploy interventions (e.g., laser leveling in District A)

Year 2: 
  ├─ Satellite measures evaporation in upgraded fields
  ├─ Satellite measures evaporation in nearby, unupgraded fields
  ├─ Compare: Upgraded vs. Not Upgraded
  ├─ Calculate: Actual water saved
  └─ Compare to prediction: Did our model work?
```

### What Gets Measured

| Metric | Before Upgrade | After Upgrade | Actual Savings |
|--------|----------------|---------------|----------------|
| Evaporation Rate | 120 mm/season | 95 mm/season | 25 mm/season |
| Water Lost | 12 Mm³/year | 9.5 Mm³/year | 2.5 Mm³/year |
| Confidence | Satellite data | Satellite data | **Verified by satellite** ✓ |

This creates an **honest, cheap way** to prove exactly how much water was actually saved—no need for expensive ground surveys or trust-based reporting.

---

## 🎯 The Complete Picture: Data → Math → Results → Verification

```
┌─────────────────────────────────────────────────────────────┐
│              FREE SATELLITE DATA (WaPOR)                   │
│         Every 10 days, every field, every year             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  STEP 1: DATA CLEANUP │
         │  • Sum 18 dekads      │
         │  • Filter desert      │
         │  • Remove open water  │
         └──────────┬────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │  STEP 2: THREE-LINE MATH │
        │  • Recoverable water (V) │
        │  • Annual cost (C)       │
        │  • Cost per m³ (κ)       │
        └──────────┬───────────────┘
                   │
                   ▼
      ┌──────────────────────────────┐
      │  STEP 3: GREEDY ALGORITHM    │
      │  Sort by cheapest water first│
      │  Spend until budget runs out │
      └──────────┬───────────────────┘
                 │
                 ▼
     ┌─────────────────────────────────┐
     │    FUNDING RECOMMENDATIONS      │
     │  District A: $100k → 12.5 Mm³   │
     │  District B: $100k → 8.3 Mm³    │
     │  District C: $100k → 5.6 Mm³    │
     │        ...                      │
     │  TOTAL: 33.3 Mm³ saved (25% up) │
     └──────────┬──────────────────────┘
                │
                ▼
  ┌──────────────────────────────────────┐
  │  DEPLOY & VERIFY (Next season)      │
  │  Satellite measures actual savings   │
  │  Compare to prediction               │
  │  Adjust model if needed              │
  └──────────────────────────────────────┘
```

---

## 💬 Key Takeaways

✅ **Transparent:** Every step uses free, public satellite data. No guesswork.

✅ **Simple:** Just three lines of math. Anyone can understand and verify it.

✅ **Optimal:** Mathematically guaranteed to save the most water per dollar spent.

✅ **Flexible:** Built-in "equity floor" slider lets politics and math coexist.

✅ **Honest:** Next season's satellites verify whether it actually worked.

---

📞 **Questions?** Would you like to dive deeper into any step—like how WaPOR measures evaporation, or how the equity floor algorithm works in detail?
