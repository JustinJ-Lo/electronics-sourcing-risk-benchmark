from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHART_DIR = BASE_DIR / "outputs" / "charts"
TABLE_DIR = BASE_DIR / "outputs" / "tables"

CHART_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


def load_latest_exposure() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / "latest_country_exposure.csv")
    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    return df


def compute_hhi(shares: pd.Series) -> float:
    return float((shares ** 2).sum())


def simulate_targeted_reallocation(
    df: pd.DataFrame,
    disrupted_country: str,
    shock_pct: float,
    target_weights: Dict[str, float],
    scenario_name: str,
) -> Dict[str, object]:
    base = df[["country", "country_share"]].copy().reset_index(drop=True)

    if disrupted_country not in base["country"].values:
        raise ValueError(f"{disrupted_country} not found in latest exposure table.")

    missing_targets = [c for c in target_weights if c not in base["country"].values]
    if missing_targets:
        raise ValueError(f"Targets not found in exposure table: {missing_targets}")

    baseline_hhi = compute_hhi(base["country_share"])

    disrupted_idx = base.index[base["country"] == disrupted_country][0]
    original_share = float(base.loc[disrupted_idx, "country_share"])
    lost_share = original_share * shock_pct

    # Reduce disrupted country share
    base.loc[disrupted_idx, "country_share"] = original_share * (1 - shock_pct)

    # Normalize target weights
    total_weight = sum(target_weights.values())
    norm_weights = {k: v / total_weight for k, v in target_weights.items()}

    # Reallocate lost share to specific substitute countries
    for target_country, weight in norm_weights.items():
        idx = base.index[base["country"] == target_country][0]
        base.loc[idx, "country_share"] += lost_share * weight

    shocked_hhi = compute_hhi(base["country_share"])

    return {
        "scenario_type": scenario_name,
        "country": disrupted_country,
        "shock_pct": shock_pct,
        "baseline_hhi": baseline_hhi,
        "shocked_hhi": shocked_hhi,
        "delta_hhi": shocked_hhi - baseline_hhi,
        "lost_share": lost_share,
        "reallocation_targets": ", ".join(target_weights.keys()),
    }


def simulate_multi_country_shock(
    df: pd.DataFrame,
    shocked_countries: List[str],
    shock_pct: float,
    target_weights: Dict[str, float],
    scenario_name: str,
) -> Dict[str, object]:
    base = df[["country", "country_share"]].copy().reset_index(drop=True)

    missing_shocks = [c for c in shocked_countries if c not in base["country"].values]
    if missing_shocks:
        raise ValueError(f"Shocked countries not found in exposure table: {missing_shocks}")

    missing_targets = [c for c in target_weights if c not in base["country"].values]
    if missing_targets:
        raise ValueError(f"Targets not found in exposure table: {missing_targets}")

    baseline_hhi = compute_hhi(base["country_share"])

    total_lost_share = 0.0
    for shocked_country in shocked_countries:
        idx = base.index[base["country"] == shocked_country][0]
        original_share = float(base.loc[idx, "country_share"])
        lost_share = original_share * shock_pct
        total_lost_share += lost_share
        base.loc[idx, "country_share"] = original_share * (1 - shock_pct)

    total_weight = sum(target_weights.values())
    norm_weights = {k: v / total_weight for k, v in target_weights.items()}

    for target_country, weight in norm_weights.items():
        idx = base.index[base["country"] == target_country][0]
        base.loc[idx, "country_share"] += total_lost_share * weight

    shocked_hhi = compute_hhi(base["country_share"])

    return {
        "scenario_type": scenario_name,
        "country": ", ".join(shocked_countries),
        "shock_pct": shock_pct,
        "baseline_hhi": baseline_hhi,
        "shocked_hhi": shocked_hhi,
        "delta_hhi": shocked_hhi - baseline_hhi,
        "lost_share": total_lost_share,
        "reallocation_targets": ", ".join(target_weights.keys()),
    }


def build_scenarios(df: pd.DataFrame) -> pd.DataFrame:
    scenario_rows = []

    # Taiwan disruption -> mostly substitute with Korea, Malaysia, Vietnam
    if "TAIWAN" in df["country"].values:
        scenario_rows.append(
            simulate_targeted_reallocation(
                df=df,
                disrupted_country="TAIWAN",
                shock_pct=0.30,
                target_weights={
                    "KOREA, SOUTH": 0.45,
                    "MALAYSIA": 0.30,
                    "VIETNAM": 0.25,
                },
                scenario_name="30pct_taiwan_disruption_targeted_reallocation",
            )
        )

        scenario_rows.append(
            simulate_targeted_reallocation(
                df=df,
                disrupted_country="TAIWAN",
                shock_pct=0.10,
                target_weights={
                    "MALAYSIA": 0.40,
                    "VIETNAM": 0.35,
                    "KOREA, SOUTH": 0.25,
                },
                scenario_name="10pct_taiwan_diversification_to_asia_alternatives",
            )
        )

    # China disruption -> shift toward Vietnam, Mexico, Malaysia
    if "CHINA" in df["country"].values:
        scenario_rows.append(
            simulate_targeted_reallocation(
                df=df,
                disrupted_country="CHINA",
                shock_pct=0.25,
                target_weights={
                    "VIETNAM": 0.40,
                    "MALAYSIA": 0.30,
                    "MEXICO": 0.30,
                },
                scenario_name="25pct_china_disruption_shift_to_vietnam_malaysia_mexico",
            )
        )

    # Korea disruption -> shift to Taiwan + Malaysia
    if "KOREA, SOUTH" in df["country"].values and "TAIWAN" in df["country"].values:
        scenario_rows.append(
            simulate_targeted_reallocation(
                df=df,
                disrupted_country="KOREA, SOUTH",
                shock_pct=0.20,
                target_weights={
                    "TAIWAN": 0.60,
                    "MALAYSIA": 0.40,
                },
                scenario_name="20pct_korea_disruption_shift_to_taiwan_malaysia",
            )
        )

    # ASEAN logistics bottleneck: Vietnam + Malaysia both hit
    asean_shock_countries = [c for c in ["VIETNAM", "MALAYSIA"] if c in df["country"].values]
    asean_targets = {k: v for k, v in {"TAIWAN": 0.45, "KOREA, SOUTH": 0.35, "MEXICO": 0.20}.items() if k in df["country"].values}
    if len(asean_shock_countries) == 2 and asean_targets:
        scenario_rows.append(
            simulate_multi_country_shock(
                df=df,
                shocked_countries=asean_shock_countries,
                shock_pct=0.15,
                target_weights=asean_targets,
                scenario_name="15pct_asean_logistics_bottleneck_shift_to_taiwan_korea_mexico",
            )
        )

    return pd.DataFrame(scenario_rows)


def chart_scenario_deltas(scenarios: pd.DataFrame) -> None:
    plot_df = scenarios.sort_values("delta_hhi", ascending=True).copy()

    plt.figure(figsize=(11, 6))
    plt.barh(plot_df["scenario_type"], plot_df["delta_hhi"])
    plt.xlabel("Change in HHI")
    plt.ylabel("Scenario")
    plt.title("Concentration Impact of Targeted Sourcing Scenarios")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "scenario_hhi_impact.png", dpi=300)
    plt.close()


def main() -> None:
    latest_exposure = load_latest_exposure()
    scenarios = build_scenarios(latest_exposure)

    scenarios.to_csv(TABLE_DIR / "scenario_analysis.csv", index=False)
    chart_scenario_deltas(scenarios)

    print(f"Saved: {TABLE_DIR / 'scenario_analysis.csv'}")
    print(f"Saved: {CHART_DIR / 'scenario_hhi_impact.png'}")
    print("\nScenario results:")
    print(scenarios.to_string(index=False))


if __name__ == "__main__":
    main()