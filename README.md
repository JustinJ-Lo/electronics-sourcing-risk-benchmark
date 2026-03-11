# Country- and Component-Level Sourcing Risk Analysis for Electronics Components

A side project I built to get closer to procurement analytics. I wanted something resume-worthy that used real public data and answered a question a supply chain team would actually care about.

---

## Executive Summary

This project analyzes U.S. sourcing concentration for semiconductor and electronics components using public Census trade data and component-level HS6 product codes.

The broad NAICS view suggested moderate concentration, but the component-level analysis shows a much sharper pattern: several core electronics categories are dominated by a small number of supplier countries, with Taiwan emerging as the leading source for most integrated-circuit categories and China leading printed circuits.

### Key Findings

- **Memory integrated circuits are the most concentrated component in the basket.** Taiwan, South Korea, and Japan account for roughly **83.6%** of U.S. memory IC imports, and the category is highly concentrated by HHI.
- **Processors/controllers are also heavily dependent on a narrow supplier base.** Taiwan alone supplies about **39.0%**, with Malaysia and Israel as the next largest sources.
- **Printed circuits follow a different sourcing pattern.** China is the dominant supplier at about **34.7%**, followed by Taiwan and South Korea, showing that component risk varies across the electronics stack.
- **Not all components carry the same level of sourcing risk.** In this basket, concentration ranges from **highly concentrated** for memory ICs to **unconcentrated** for amplifier ICs.

![Dominant Supplier Country by Electronics Component](https://raw.githubusercontent.com/JustinJ-Lo/electronics-sourcing-risk-benchmark/main/outputs/charts/dominant_supplier_country_by_component.png)


## The Question

Where does the U.S. source semiconductors and electronic components from, how dependent is it on a handful of countries, and has that concentration gotten better or worse over time?

---

## What I Found

**Concentration has been creeping up.** HHI scores trend upward from 2023 through 2025 — not alarming, but directionally important. Fewer countries are quietly absorbing more of the sourcing share.

**HHI (Herfindahl–Hirschman Index)** is a concentration measure: higher values mean sourcing is more dependent on fewer countries.

![Concentration Trend](https://raw.githubusercontent.com/JustinJ-Lo/electronics-sourcing-risk-benchmark/main/outputs/charts/concentration_trend.png)

**Asian import prices dropped after 2022, but domestic producer prices kept rising.** The cost story shifted — what had been import-side pressure increasingly showed up in domestic production instead.

![Price Trends](https://raw.githubusercontent.com/JustinJ-Lo/electronics-sourcing-risk-benchmark/main/outputs/charts/price_index_trends_rebased.png)


**Top sourcing countries remain concentrated in Asia-Pacific manufacturing hubs.** Taiwan, South Korea, Vietnam, Malaysia, and ASEAN-linked supplier regions continue to dominate the landscape, reinforcing how geographically concentrated semiconductor production still is.

![Top Countries](https://raw.githubusercontent.com/JustinJ-Lo/electronics-sourcing-risk-benchmark/main/outputs/charts/top_10_countries_latest_month.png)

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

## Latest Component Supplier Summary

| HS6 Code | Component | Top Supplier | Top Supplier Share | Top 3 Supplier Share | Risk Band |
|---|---|---:|---:|---:|---|
| 854232 | Memory ICs | Taiwan | 40.7% | 83.6% | Highly concentrated |
| 854231 | Processors / Controllers | Taiwan | 39.0% | 76.5% | Moderately concentrated |
| 853400 | Printed Circuits | China | 34.7% | 64.2% | Moderately concentrated |
| 854239 | Other ICs | Taiwan | 33.5% | 58.4% | Moderately concentrated |
| 854233 | Amplifier ICs | Taiwan | 28.9% | 55.6% | Unconcentrated |

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