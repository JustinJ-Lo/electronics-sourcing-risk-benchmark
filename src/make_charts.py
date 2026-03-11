from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHART_DIR = BASE_DIR / "outputs" / "charts"
TABLE_DIR = BASE_DIR / "outputs" / "tables"

CHART_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    analytical = pd.read_csv(PROCESSED_DIR / "analytical_dataset.csv")
    concentration = pd.read_csv(PROCESSED_DIR / "monthly_concentration_metrics.csv")
    latest_exposure = pd.read_csv(PROCESSED_DIR / "latest_country_exposure.csv")

    analytical["month"] = pd.to_datetime(analytical["month"], errors="coerce")
    concentration["month"] = pd.to_datetime(concentration["month"], errors="coerce")
    latest_exposure["month"] = pd.to_datetime(latest_exposure["month"], errors="coerce")

    return analytical, concentration, latest_exposure


def chart_top_countries_latest_month(latest_exposure: pd.DataFrame) -> None:
    latest_month = latest_exposure["month"].max()
    top10 = (
        latest_exposure.sort_values("country_share", ascending=False)
        .head(10)
        .sort_values("country_share", ascending=True)
    )

    top10.to_csv(TABLE_DIR / "top_10_countries_latest_month.csv", index=False)

    plt.figure(figsize=(10, 6))
    plt.barh(top10["country"], top10["country_share_pct"])
    plt.xlabel("Share of U.S. Imports (%)")
    plt.ylabel("Country")
    plt.title(f"Top 10 Source Countries — {latest_month.strftime('%Y-%m')}")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "top_10_countries_latest_month.png", dpi=300)
    plt.close()


def chart_hhi_trend(concentration: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(concentration["month"], concentration["hhi"], label="HHI")
    plt.plot(concentration["month"], concentration["c5_share"], label="Top-5 Share")
    plt.xlabel("Month")
    plt.ylabel("Concentration Metric")
    plt.title("Sourcing Concentration Over Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_DIR / "concentration_trend.png", dpi=300)
    plt.close()


def chart_price_indexes_rebased(analytical: pd.DataFrame) -> None:
    price_cols = [
        "import_price_index_overall",
        "import_price_index_asian_nics",
        "import_price_index_industrialized",
        "domestic_producer_price_index",
    ]

    price_df = (
        analytical[["month"] + price_cols]
        .drop_duplicates(subset=["month"])
        .sort_values("month")
        .dropna()
    )

    rebased = price_df.copy()
    for col in price_cols:
        rebased[col] = rebased[col] / rebased[col].iloc[0] * 100

    plt.figure(figsize=(10, 6))
    for col in price_cols:
        plt.plot(rebased["month"], rebased[col], label=col)

    plt.xlabel("Month")
    plt.ylabel("Rebased Index (Start = 100)")
    plt.title("Price Index Trends (Rebased for Comparability)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_DIR / "price_index_trends_rebased.png", dpi=300)
    plt.close()


def chart_latest_volatility(latest_exposure: pd.DataFrame) -> None:
    top10 = (
        latest_exposure.sort_values("country_share", ascending=False)
        .head(10)
        .sort_values("share_volatility_12m_pct", ascending=True)
    )

    plt.figure(figsize=(10, 6))
    plt.barh(top10["country"], top10["share_volatility_12m_pct"])
    plt.xlabel("12-Month Share Volatility (percentage points)")
    plt.ylabel("Country")
    plt.title("Volatility of Sourcing Share — Top Countries")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "top_country_share_volatility.png", dpi=300)
    plt.close()


def main() -> None:
    print("Loading processed data...")
    analytical, concentration, latest_exposure = load_data()

    print("Making top-country chart...")
    chart_top_countries_latest_month(latest_exposure)

    print("Making concentration chart...")
    chart_hhi_trend(concentration)

    print("Making rebased price chart...")
    chart_price_indexes_rebased(analytical)

    print("Making volatility chart...")
    chart_latest_volatility(latest_exposure)

    print("\nSaved charts to outputs/charts/")
    print("Saved summary table to outputs/tables/")


if __name__ == "__main__":
    main()