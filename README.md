# Sourcing Risk Analysis for Electronics Components

This is a side project I built because I wanted to better understand how concentrated U.S. electronics sourcing really is at the component level.

I'm interested in procurement analytics, supply chains, and East Asian manufacturing networks, especially in industries like electronics and robotics. A lot of the time, sourcing risk gets discussed at a broad industry level, but I wanted to look at the actual component categories where dependence might be much higher.

---

## The Short Version

Looking only at the broad industry level can make sourcing concentration seem more manageable than it really is. Once I broke the data down to the HS6 component level, a clearer pattern showed up: some important electronics categories depend heavily on just a few countries.

For example, Taiwan plays a major role in several integrated-circuit categories, China is a leading supplier in printed circuits, and concentration in some of these categories has been rising over time.

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

### Broad industry averages hide some of the real risk

At the NAICS 3344 level, concentration looks only moderate. But when I looked at specific component categories, the picture became more uneven. Memory ICs and processors look much more concentrated than the broader industry numbers would suggest.

### Concentration has generally been moving upward

From 2023 through 2025, HHI trends upward in the data. I would not interpret that as proof of an immediate sourcing crisis, but it does suggest that dependence on a smaller set of countries has been increasing rather than decreasing.

![Concentration Trend](./outputs/charts/concentration_trend.png)

### Price pressure changed form rather than disappearing

After 2022, Asian import prices came down, but domestic producer prices stayed elevated. To me, that suggests the cost pressure did not really go away. It just shifted.

![Price Trends](./outputs/charts/price_index_trends_rebased.png)

### The supplier base is still heavily concentrated in Asia-Pacific

Taiwan, South Korea, Vietnam, Malaysia, and nearby suppliers show up repeatedly across the categories I looked at. The exact shares vary by product, but the regional pattern is pretty consistent.

![Top Countries](./outputs/charts/top_10_countries_latest_month.png)

---

## What This Means for Sourcing

I do not see this project as a full sourcing decision model. It is more of a way to flag where concentration looks high enough that a procurement team might want to look more closely.

**HS6-level concentration can be much sharper than aggregate numbers suggest.** A company might seem reasonably diversified at the industry level while still being very exposed in a few key components.

**Memory ICs and processors look like the most exposed categories in this sample.** If a disruption affects one of the dominant supplier countries, the impact could be much larger in these categories than in others.

**Different components have different risk profiles.** That was one of the more interesting takeaways for me. Electronics sourcing does not look uniform across categories, so sourcing strategy probably should not be uniform either.

### Taiwan Disruption Scenario

To make the concentration numbers more concrete, I modeled a simple scenario where Taiwan's semiconductor exports for memory ICs (HS6 854232) fall by 50%.

Since Taiwan currently supplies about 40% of U.S. memory IC imports in the data, a 50% reduction would remove about 20% of available supply in the short run, assuming other suppliers could not immediately replace it.

![Memory IC Supply Exposure Under Taiwan Shock](./outputs/charts/taiwan_shock_memory_ics.png)

The chart below looks at how much supply would need to be replaced and uses current supplier shares as a rough proxy for replacement capacity. This is obviously simplified, since in real life substitution would depend on fabrication capacity, qualification timelines, contracts, and how quickly suppliers could redirect shipments.

![Potential Replacement Capacity](./outputs/charts/taiwan_supply_replacement_capacity.png)

![Scenario HHI Impact](./outputs/charts/scenario_hhi_impact.png)

### Cost vs. Risk Tradeoff

I also added a simple landed-cost scenario comparing supplier countries across unit cost, shipping, tariffs, and a basic risk premium.

This is not meant to be a real quote model. I included it more as a way to show the tradeoff: the cheapest supplier is not always the lowest-risk supplier, and sourcing decisions usually involve balancing both.

![Cost vs. Risk Tradeoff](./outputs/charts/cost_vs_risk_tradeoff.png)

---

## Data Sources

- **U.S. Census International Trade API** — monthly imports by country, NAICS 3344
- **U.S. Census International Trade API** — HS6 component-level trade flows for selected electronics categories
- **FRED / BLS** — import price indexes and domestic producer price index series

Everything in this project uses public data, and the workflow can be reproduced from the scripts in the repo.

---

## How the Pipeline Works

The project can be run end to end with:

```bash
python3 src/run_pipeline.py
```

The pipeline includes data collection, dataset construction, scenario analysis, clustering, and chart generation.

Main scripts:

- `fetch_data.py`
- `fetch_fred_api.py`
- `fetch_hs_components.py`
- `build_dataset.py`
- `analyze_hs_components.py`
- `scenario_analysis.py`
- `supply_shock_simulation.py`
- `supplier_cost_model.py`
- `cluster_component_risk.py`
- `make_charts.py`

I also added a simple clustering step using `hhi`, `c3_share`, and `supplier_count` to group components into four risk segments:

- Lower concentration / broad supplier base
- Lower concentration / moderate breadth
- Elevated concentration
- Highest concentration / dominant suppliers

I used this more as a monitoring and prioritization tool than as a predictive model.

---

## Repo Structure

```
electronics-sourcing-risk-benchmark/
├── README.md
├── FINDINGS.md
├── requirements.txt
├── .github/
│   └── workflows/
│       └── monthly_refresh.yml
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
│   ├── charts/
│   └── tables/
└── src/
    ├── fetch_data.py
    ├── fetch_fred_api.py
    ├── fetch_hs_components.py
    ├── build_dataset.py
    ├── analyze_hs_components.py
    ├── scenario_analysis.py
    ├── supply_shock_simulation.py
    ├── supplier_cost_model.py
    ├── cluster_component_risk.py
    ├── make_charts.py
    └── run_pipeline.py
```