"""
Shared configuration for the Nile Delta evaporation-hotspot targeting pipeline.

WaPOR Hackathon 2026 - Team 39 - "From tools to decisions"

Everything a user might want to change lives here.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_INTERIM = ROOT / "data" / "interim"
WEBMAP_DATA = ROOT / "webmap" / "data"
for _p in (DATA_RAW, DATA_INTERIM, WEBMAP_DATA):
    _p.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# Study area
# ----------------------------------------------------------------------------
COUNTRY_A3 = "EGY"

# Natural Earth admin-1 names (as they appear in ne_10m_admin_1_states_provinces)
# grouped by the agro-hydrological system they belong to.
DELTA_RICE = [        # Northern Delta - ponded rice belt, high open-water evaporation
    "Kafr ash Shaykh", "Ad Daqahliyah", "Al Buhayrah", "Ash Sharqiyah", "Dumyat",
]
DELTA_OTHER = [       # Southern / central Delta - cotton, maize, berseem, horticulture
    "Al Gharbiyah", "Al Minufiyah", "Al Qalyubiyah", "Al Iskandariyah",
    "Bur Sa`id", "Al Isma`iliyah",
]
VALLEY = [            # Nile Valley - narrow strip, sugarcane / wheat / maize
    "Al Jizah", "Bani Suwayf", "Al Fayyum", "Al Minya", "Asyut",
    "Suhaj", "Qina", "Luxor", "Aswan",
]
STUDY_GOVERNORATES = DELTA_RICE + DELTA_OTHER + VALLEY

SYSTEM_OF = {}
for _n in DELTA_RICE:
    SYSTEM_OF[_n] = "Delta - rice belt"
for _n in DELTA_OTHER:
    SYSTEM_OF[_n] = "Delta - other"
for _n in VALLEY:
    SYSTEM_OF[_n] = "Nile Valley"

# English display names (Natural Earth uses a transliteration few Egyptians use)
DISPLAY_NAME = {
    "Kafr ash Shaykh": "Kafr El Sheikh", "Ad Daqahliyah": "Dakahlia",
    "Al Buhayrah": "Beheira", "Ash Sharqiyah": "Sharqia", "Dumyat": "Damietta",
    "Al Gharbiyah": "Gharbia", "Al Minufiyah": "Menoufia",
    "Al Qalyubiyah": "Qalyubia", "Al Iskandariyah": "Alexandria",
    "Bur Sa`id": "Port Said", "Al Isma`iliyah": "Ismailia",
    "Al Jizah": "Giza", "Bani Suwayf": "Beni Suef", "Al Fayyum": "Fayoum",
    "Al Minya": "Minya", "Asyut": "Assiut", "Suhaj": "Sohag",
    "Qina": "Qena", "Luxor": "Luxor", "Aswan": "Aswan",
}

# ----------------------------------------------------------------------------
# Cultivated area, thousand feddan (1 feddan = 0.42 ha)
# ----------------------------------------------------------------------------
# APPROXIMATE PLANNING FIGURES ONLY. Order of magnitude is right and the relative
# ranking between governorates is right, but these are not official statistics.
# Replace with MALR / CAPMAS "Agricultural Statistics Bulletin" cropped-area
# figures before any number leaves the team. Tracked in docs/ASSUMPTIONS.md.
FEDDAN_TO_HA = 0.42
CULTIVATED_KFEDDAN = {
    "Al Buhayrah": 1020, "Ash Sharqiyah": 900, "Ad Daqahliyah": 760,
    "Kafr ash Shaykh": 610, "Al Gharbiyah": 410, "Al Minufiyah": 350,
    "Al Qalyubiyah": 200, "Al Isma`iliyah": 250, "Dumyat": 105,
    "Al Iskandariyah": 100, "Bur Sa`id": 50,
    "Al Minya": 620, "Suhaj": 420, "Asyut": 400, "Al Fayyum": 400,
    "Bani Suwayf": 300, "Qina": 300, "Al Jizah": 200, "Aswan": 150,
    "Luxor": 100,
}

# ----------------------------------------------------------------------------
# Season definition
# ----------------------------------------------------------------------------
SEASON_LABEL = "Summer (Nili/Sefi) 2024"
SEASON_START = "2024-05-01"
SEASON_END = "2024-10-31"

# ----------------------------------------------------------------------------
# WaPOR v3 mapsets used
# ----------------------------------------------------------------------------
# Level 2 = 100 m. The Nile River Basin is published as its own WaPOR v3 region,
# which is why we can work at 100 m rather than the 300 m global product.
WAPOR_LEVEL = "L2"
WAPOR_VARIABLES = {
    "AETI": "Actual evapotranspiration and interception",
    "E":    "Evaporation",
    "T":    "Transpiration",
    "I":    "Interception",
    "RET":  "Reference evapotranspiration",
}
# wapordl region code. "EGY" gives the national 100 m product.
WAPOR_REGION = "EGY"

# ----------------------------------------------------------------------------
# Intervention cost model  <-- THE ASSUMPTIONS THE JURY WILL PROBE
# ----------------------------------------------------------------------------
# These are literature-order estimates, NOT measurements. They are deliberately
# exposed as editable inputs in the web map so a user can substitute their own.
# e_reduction = fraction of soil/open-water evaporation avoided by the measure.
# life_years  = amortisation period for the capital cost.
INTERVENTIONS = {
    "laser_levelling": {
        "label": "Laser land levelling",
        "usd_per_ha": 75, "life_years": 5, "e_reduction": 0.10,
        "seasons_per_year": 2,
        "applies_to": ["Delta - rice belt", "Delta - other", "Nile Valley"],
        "note": ("Reduces ponding depth and over-irrigation of high spots, so "
                 "less standing water and less saturated soil surface. Already "
                 "deployed at scale in Egypt, so cost and effect are the best "
                 "constrained of the four. Benefits both summer and winter crops."),
    },
    "awd": {
        "label": "Alternate wetting & drying (rice)",
        "usd_per_ha": 25, "life_years": 1, "e_reduction": 0.10,
        "seasons_per_year": 1,
        "applies_to": ["Delta - rice belt"],
        "note": ("Training + field water tubes. IMPORTANT: AWD's headline saving "
                 "in the literature is in water APPLIED - percolation and seepage - "
                 "not in evapotranspiration. In the closed, high-reuse Delta, "
                 "percolation is largely recovered downstream, so we deliberately "
                 "exclude it and count ONLY the evaporation component: removing "
                 "the free water surface for part of the season. Hence 10%, not "
                 "the 25-30% quoted for total water application."),
    },
    "mulching": {
        "label": "Straw / plastic mulching",
        "usd_per_ha": 260, "life_years": 1, "e_reduction": 0.30,
        "seasons_per_year": 1,
        "applies_to": ["Delta - other", "Nile Valley"],
        "note": ("Suppresses bare-soil evaporation between rows. Caveat: some of "
                 "the conserved soil water is taken up and transpired instead, "
                 "converting E to T and yield rather than to saved water - good "
                 "agronomy, zero water volume. Treat as an upper bound."),
    },
    "drip_retrofit": {
        "label": "Drip retrofit",
        "usd_per_ha": 1800, "life_years": 10, "e_reduction": 0.45,
        "seasons_per_year": 2,
        "applies_to": ["Delta - other", "Nile Valley"],
        "note": ("Largest saving, largest capital cost, and the same E-to-T "
                 "compensation caveat as mulching. Not viable for paddy rice."),
    },
}

DEFAULT_BUDGET_USD = 12_000_000   # a plausible annual on-farm modernisation line
