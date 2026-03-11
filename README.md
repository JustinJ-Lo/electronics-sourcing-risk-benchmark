# Electronics Component Sourcing Risk & Cost Pressure Benchmark

A side project I built to get closer to procurement analytics. I wanted something resume-worthy that used real public data and answered a question a supply chain team would actually care about.

---

## The Question

Where does the U.S. source semiconductors and electronic components from, how dependent are we on a handful of countries, and has that gotten better or worse?

---

## What I Found

**Concentration has been creeping up.** HHI scores trend upward from 2023 through 2025 — not alarming, but the direction matters. Fewer countries are quietly absorbing more of the sourcing share.

**Asian import prices dropped after 2022, but domestic producer prices kept rising.** The cost story shifted — what used to be pressure from import markets started showing up in domestic production instead.

**The top sourcing countries are exactly who you'd expect:** Taiwan, South Korea, Vietnam, Malaysia, and other ASEAN countries. The Asia-Pacific grip on semiconductor manufacturing is still very much intact.

---

## Data Sources

- **U.S. Census International Trade API** — monthly imports by country, NAICS 3344 (Semiconductor and Electronic Component Manufacturing)
- **FRED / BLS** — import price index for NAICS 3344, Asian NIC origin prices, industrialized-country prices, domestic producer price index

All public data, all reproducible.

---

## How It Works

Three scripts, run in order:

1. `fetch_data.py` — pulls Census and FRED data
2. `build_dataset.py` — computes country shares, 3-month moving averages, HHI
3. `make_charts.py` — generates the charts

---

## Repo Structure
```
electronics-sourcing-risk-benchmark/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
│   ├── charts/
│   └── tables/
└── src/
    ├── fetch_data.py
    ├── build_dataset.py
    └── make_charts.py
```

---

## Resume Bullet

Built a procurement-focused benchmarking analysis using U.S. Census trade data and BLS price indexes to measure semiconductor sourcing concentration and regional cost pressure — quantifying HHI risk trends and supplier-region price divergence using Python.