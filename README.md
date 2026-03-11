# Electronics Component Sourcing Risk & Cost Pressure Benchmark

A side project I built to get closer to procurement analytics. I wanted something resume-worthy that used real public data and answered a question a supply chain team would actually care about.

---

## The Question

Where does the U.S. source semiconductors and electronic components from, how dependent is it on a handful of countries, and has that concentration gotten better or worse over time?

---

## What I Found

**Concentration has been creeping up.** HHI scores trend upward from 2023 through 2025 — not alarming, but directionally important. Fewer countries are quietly absorbing more of the sourcing share.

**HHI (Herfindahl–Hirschman Index)** is a concentration measure: higher values mean sourcing is more dependent on fewer countries.

![HHI Trend](outputs/charts/hhi_trend.png)

**Asian import prices dropped after 2022, but domestic producer prices kept rising.** The cost story shifted — what had been import-side pressure increasingly showed up in domestic production instead.

![Price Trends](outputs/charts/price_index_trends.png)

**Top sourcing countries remain concentrated in Asia-Pacific manufacturing hubs.** Taiwan, South Korea, Vietnam, Malaysia, and ASEAN-linked supplier regions continue to dominate the landscape, reinforcing how geographically concentrated semiconductor production still is.

![Top Countries](outputs/charts/top_10_countries_latest_month.png)

---

## Data Sources

- **U.S. Census International Trade API** — monthly imports by country, NAICS 3344 (Semiconductor and Electronic Component Manufacturing)
- **FRED / BLS** — import price index for NAICS 3344, Asian NIC origin prices, industrialized-country prices, domestic producer price index

All public data, all reproducible.

---

## How It Works

Three scripts, run in order:

1. `fetch_data.py` — pulls Census and FRED data  
2. `build_dataset.py` — computes country shares, 3-month moving averages, and HHI  
3. `make_charts.py` — generates the charts

---

## Repo Structure

```text
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