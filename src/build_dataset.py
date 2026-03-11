from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    imports = pd.read_csv(RAW_DIR / "census_imports_naics_3344.csv")
    fred = pd.read_csv(RAW_DIR / "fred_price_indexes_3344.csv")

    imports["time"] = pd.to_datetime(imports["time"], errors="coerce")
    imports["GEN_VAL_MO"] = pd.to_numeric(imports["GEN_VAL_MO"], errors="coerce")

    fred["date"] = pd.to_datetime(fred["date"], errors="coerce")

    return imports, fred


def build_country_month_panel(imports: pd.DataFrame) -> pd.DataFrame:
    df = imports.copy()

    df = df.rename(columns={"CTY_NAME": "country", "GEN_VAL_MO": "import_value"})
    df["month"] = df["time"].dt.to_period("M").dt.to_timestamp()

    # Monthly total imports across all countries
    monthly_totals = (
        df.groupby("month", as_index=False)["import_value"]
        .sum()
        .rename(columns={"import_value": "total_import_value"})
    )

    df = df.merge(monthly_totals, on="month", how="left")
    df["country_share"] = df["import_value"] / df["total_import_value"]

    # Sort for rolling calculations
    df = df.sort_values(["country", "month"]).reset_index(drop=True)

    # 3-month moving average of country share
    df["country_share_ma3"] = (
        df.groupby("country")["country_share"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )

    return df


def build_hhi(panel: pd.DataFrame) -> pd.DataFrame:
    hhi = (
        panel.groupby("month", as_index=False)["country_share"]
        .apply(lambda s: (s ** 2).sum())
        .rename(columns={"country_share": "hhi"})
    )
    return hhi


def prepare_fred_panel(fred: pd.DataFrame) -> pd.DataFrame:
    df = fred.copy()
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

    keep_cols = [
        "month",
        "import_price_index_overall",
        "import_price_index_asian_nics",
        "import_price_index_industrialized",
        "domestic_producer_price_index",
    ]

    df = df[keep_cols].drop_duplicates(subset=["month"]).sort_values("month")
    return df


def main() -> None:
    print("Loading raw data...")
    imports, fred = load_raw_data()

    print("Building country-month panel...")
    panel = build_country_month_panel(imports)

    print("Calculating HHI...")
    hhi = build_hhi(panel)

    print("Preparing FRED panel...")
    fred_panel = prepare_fred_panel(fred)

    print("Merging analytical dataset...")
    analytical = panel.merge(hhi, on="month", how="left")
    analytical = analytical.merge(fred_panel, on="month", how="left")

    analytical = analytical.sort_values(["month", "import_value"], ascending=[True, False])

    panel_path = PROCESSED_DIR / "country_month_panel.csv"
    hhi_path = PROCESSED_DIR / "monthly_hhi.csv"
    analytical_path = PROCESSED_DIR / "analytical_dataset.csv"

    panel.to_csv(panel_path, index=False)
    hhi.to_csv(hhi_path, index=False)
    analytical.to_csv(analytical_path, index=False)

    print(f"Saved: {panel_path}")
    print(f"Saved: {hhi_path}")
    print(f"Saved: {analytical_path}")

    latest_month = analytical["month"].max()
    latest_top = (
        analytical[analytical["month"] == latest_month]
        .sort_values("import_value", ascending=False)
        [["month", "country", "import_value", "country_share", "country_share_ma3", "hhi"]]
        .head(10)
    )

    print("\nTop 10 countries in latest month:")
    print(latest_top.to_string(index=False))

    print("\nDone.")
    print(f"Panel rows:      {len(panel):,}")
    print(f"HHI rows:        {len(hhi):,}")
    print(f"Analytical rows: {len(analytical):,}")


if __name__ == "__main__":
    main()