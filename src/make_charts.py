from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHART_DIR = BASE_DIR / "outputs" / "charts"
TABLE_DIR = BASE_DIR / "outputs" / "tables"

CHART_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    analytical = pd.read_csv(PROCESSED_DIR / "analytical_dataset.csv")
    hhi = pd.read_csv(PROCESSED_DIR / "monthly_hhi.csv")

    analytical["month"] = pd.to_datetime(analytical["month"], errors="coerce")
    hhi["month"] = pd.to_datetime(hhi["month"], errors="coerce")

    return analytical, hhi


def chart_top_countries_latest_month(analytical: pd.DataFrame) -> None:
    latest_month = analytical["month"].max()
    latest = analytical[analytical["month"] == latest_month].copy()

    top10 = (
        latest.sort_values("import_value", ascending=False)
        .loc[:, ["country", "import_value", "country_share"]]
        .head(10)
        .sort_values("import_value", ascending=True)
    )

    top10.to_csv(TABLE_DIR / "top_10_countries_latest_month.csv", index=False)

    plt.figure(figsize=(10, 6))
    plt.barh(top10["country"], top10["import_value"])
    plt.xlabel("Import Value (USD)")
    plt.ylabel("Country")
    plt.title(f"Top 10 Source Countries — {latest_month.strftime('%Y-%m')}")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "top_10_countries_latest_month.png", dpi=300)
    plt.close()


def chart_hhi_trend(hhi: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(hhi["month"], hhi["hhi"])
    plt.xlabel("Month")
    plt.ylabel("HHI")
    plt.title("Sourcing Concentration (HHI) Over Time")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "hhi_trend.png", dpi=300)
    plt.close()


def chart_price_indexes(analytical: pd.DataFrame) -> None:
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
    )

    plt.figure(figsize=(10, 6))
    for col in price_cols:
        plt.plot(price_df["month"], price_df[col], label=col)

    plt.xlabel("Month")
    plt.ylabel("Index")
    plt.title("Import and Domestic Price Index Trends")
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_DIR / "price_index_trends.png", dpi=300)
    plt.close()


def main() -> None:
    print("Loading processed data...")
    analytical, hhi = load_data()

    print("Making top-country chart...")
    chart_top_countries_latest_month(analytical)

    print("Making HHI chart...")
    chart_hhi_trend(hhi)

    print("Making price index chart...")
    chart_price_indexes(analytical)

    print("\nSaved charts to outputs/charts/")
    print("Saved summary table to outputs/tables/")


if __name__ == "__main__":
    main()