# Sourcing Risk Analysis for Electronics Components

A procurement-focused side project I built to understand how concentrated U.S. electronics sourcing actually is — not at the broad industry level, but at the component level, where the real exposure tends to hide.

The motivation was straightforward: I'm interested in procurement analytics and global manufacturing, especially East Asian supplier ecosystems relevant to electronics, robotics, and supply chains. I wanted to build something that looked like a real procurement question rather than a generic data project.

---

## The Short Version

Broad industry-level concentration can look manageable. The HS6 component view tells a more useful story. Several core electronics categories depend heavily on a small number of countries. For example, Taiwan dominates multiple integrated-circuit categories, China leads printed circuits, and that concentration has been creeping upward.

### Component Supplier Summary

| HS6 Code | Component | Top Supplier | Top Supplier Share | Top 3 Share | Risk Band |
|---|---|---:|---:|---:|---|
| 854232 | Memory ICs | Taiwan | 40.7% | 83.6% | Highly concentrated |
| 854231 | Processors / Controllers | Taiwan | 39.0% | 76.5% | Moderately concentrated |
| 853400 | Printed Circuits | China | 34.7% | 64.2% | Moderately concentrated |
| 854239 | Other ICs | Taiwan | 33.5% | 58.4% | Moderately concentrated |
| 854233 | Amplifier ICs | Taiwan | 28.9% | 55.6% | Unconcentrated |

![Dominant Supplier Country by Electronics Component](./outputs/charts/dominant_supplier_country_by_component.png)

---

## What I Found

### The aggregate view smooths over the parts that matter

At the NAICS 3344 level, concentration looks only moderate. But that's exactly the problem. Broad categories average out the component families procurement teams actually worry about. The HS6 analysis surfaces sharper concentration in memory ICs and processors than the top-line numbers suggest.

### Concentration has been drifting upward

HHI scores trend upward from 2023 through 2025. That doesn't mean a sourcing crisis is coming, but it does mean imports are becoming more dependent on fewer countries over time, not less.

![Concentration Trend](./outputs/charts/concentration_trend.png)

### Price pressure shifted, it didn't disappear

After 2022, Asian import prices fell while domestic producer prices kept rising. The cost pressure moved from the import side toward domestic production rather than resolving.

![Price Trends](./outputs/charts/price_index_trends_rebased.png)

### The geography is still firmly Asia-Pacific

Taiwan, South Korea, Vietnam, Malaysia, and neighboring ASEAN suppliers dominate across all the categories I looked at. The specific country shares vary by component, but the regional concentration is consistent throughout.

![Top Countries](./outputs/charts/top_10_countries_latest_month.png)

---

## What This Means for Sourcing

This project doesn't try to solve supplier selection or total landed cost. It's more about identifying where concentration is high enough to warrant a closer look.

**HS6-level risk is sharper than the aggregate suggests.** A company might look reasonably diversified at the industry level while still being exposed in a few specific component families. The question is which categories deserve second-source review or supplier mapping.

**Memory ICs and processors are the most exposed.** Heavy dependence in these categories means a shock to a small number of countries — trade restrictions, a fabrication bottleneck, a geopolitical event — creates outsized disruption risk.

**Printed circuits and ICs don't follow the same pattern.** Electronics sourcing isn't one uniform risk. Category strategies probably need to reflect that.

### Taiwan Disruption Scenario

To make the concentration numbers more tangible, I modeled a scenario where Taiwan semiconductor exports drop 50% for memory ICs (HS6 854232). Taiwan currently supplies roughly 40% of U.S. memory IC imports, so a 50% cut removes about 20% of available supply in the short run, assuming other suppliers can't immediately step in.

![Memory IC Supply Exposure Under Taiwan Shock](./outputs/charts/taiwan_shock_memory_ics.png)

The chart below shows how much supply would need to come from elsewhere, and what current supplier shares look like as a rough proxy for replacement capacity. In practice, this would depend on whether existing producers could scale fabrication, redirect exports, or whether alternate suppliers could be qualified in time.

![Potential Replacement Capacity](./outputs/charts/taiwan_supply_replacement_capacity.png)

![Scenario HHI Impact](./outputs/charts/scenario_hhi_impact.png)

### Cost vs. Risk Tradeoff

I also added a simple landed-cost scenario comparing supplier countries across unit cost, shipping, tariffs, and a risk premium. It's illustrative, not a quote model. However, it frames the practical tradeoff: lower-left on the chart means lower cost and lower risk, which is obviously preferable. The point is that sourcing decisions involve balancing cost efficiency against concentration exposure, and those two things don't always point the same direction.

![Cost vs. Risk Tradeoff](./outputs/charts/cost_vs_risk_tradeoff.png)

---

## Data Sources

- **U.S. Census International Trade API** — monthly imports by country, NAICS 3344
- **U.S. Census International Trade API** — HS6 component-level trade flows for selected electronics categories
- **FRED / BLS** — import price indexes (Asian NICs, industrialized countries) and domestic producer price index

Everything is public and the workflow is fully reproducible.

---

## How the Pipeline Works

The project runs as an end-to-end analytics pipeline:

```bash
python3 src/run_pipeline.py
```

Three scripts, in order:

1. `fetch_data.py` — pulls Census and FRED data via API
2. `build_dataset.py` — computes country shares, HHIs, and moving averages
3. `make_charts.py` — generates charts and summary tables

The pipeline also clusters components into four risk segments using `hhi`, `c3_share`, and `supplier_count`:

- Lower concentration / broad supplier base
- Lower concentration / moderate breadth
- Elevated concentration
- Highest concentration / dominant suppliers

This segmentation is for prioritization and monitoring,identifying which categories might deserve more procurement attention, not predicting what will happen.

---

## Repo Structure

```
electronics-sourcing-risk-benchmark/
├── README.md
├── FINDINGS.md
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