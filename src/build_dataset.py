from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

AGGREGATE_NAMES = {
    "APEC",
    "ASIA",
    "ASEAN",
    "OECD",
    "PACIFIC RIM COUNTRIES",
    "TWENTY LATIN AMERICAN REPUBLICS",
    "EUROPEAN UNION",
    "EUROPE",
    "AFRICA",
    "MIDDLE EAST",
    "NORTH AMERICA",
    "SOUTH/CENTRAL AMERICA",
    "SOUTH AMERICA",
    "CENTRAL AMERICA",
    "OTHER AFRICA",
    "OTHER ASIA, NESOI",
    "OTHER EUROPE, NESOI",
    "OTHER WESTERN HEMISPHERE",
    "USMCA (NAFTA)",
    "EURO AREA",
    "EURO AREA20",
    "OPEC",
}

AGGREGATE_PATTERNS = [
    r"COUNTRIES",
    r"REPUBLICS",
    r"\bAPEC\b",
    r"\bASEAN\b",
    r"\bOECD\b",
    r"\bOPEC\b",
    r"PACIFIC RIM",
    r"EUROPEAN UNION",
    r"EURO AREA",
    r"USMCA",
    r"NAFTA",
    r"NESOI",
    r"OTHER ",
]


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    imports = pd.read_csv(RAW_DIR / "census_imports_naics_3344.csv")
    fred = pd.read_csv(RAW_DIR / "fred_price_indexes_3344.csv")

    imports["time"] = pd.to_datetime(imports["time"], errors="coerce")
    imports["GEN_VAL_MO"] = pd.to_numeric(imports["GEN_VAL_MO"], errors="coerce")
    fred["date"] = pd.to_datetime(fred["date"], errors="coerce")

    return imports, fred


def filter_aggregate_rows(imports: pd.DataFrame) -> pd.DataFrame:
    """
    Remove aggregate trade regions (e.g. ASIA, EUROPE, NATO) so the dataset
    only contains actual sourcing locations (countries / territories).
    """

    df = imports.copy()

    # Normalize country names
    names = (
        df["CTY_NAME"]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    df["CTY_NAME"] = names

    # Known aggregate regions / blocs from Census trade data
    bad_names = {
        "AFRICA",
        "APEC",
        "ASEAN",
        "ASIA",
        "AUSTRALIA AND OCEANIA",
        "CACM",
        "CAFTA-DR",
        "CENTRAL AMERICA",
        "EURO AREA",
        "EUROPE",
        "EUROPEAN UNION",
        "LAFTA",
        "NATO",
        "NORTH AMERICA",
        "OECD",
        "PACIFIC RIM COUNTRIES",
        "SOUTH AMERICA",
        "TWENTY LATIN AMERICAN REPUBLICS",
        "USMCA (NAFTA)",
    }

    # Remove exact aggregate matches
    df = df.loc[~df["CTY_NAME"].isin(bad_names)].copy()

    # Safety validation: only flag obvious aggregate labels that should
    # never appear as real countries / territories.
    forbidden_exact = {
        "AFRICA",
        "APEC",
        "ASEAN",
        "ASIA",
        "AUSTRALIA AND OCEANIA",
        "CACM",
        "CAFTA-DR",
        "CENTRAL AMERICA",
        "EURO AREA",
        "EUROPE",
        "EUROPEAN UNION",
        "LAFTA",
        "NATO",
        "NORTH AMERICA",
        "OECD",
        "PACIFIC RIM COUNTRIES",
        "SOUTH AMERICA",
        "TWENTY LATIN AMERICAN REPUBLICS",
        "USMCA (NAFTA)",
    }

    forbidden_fragments = [
        "COUNTRIES",
        "REPUBLICS",
        "PACIFIC RIM",
        "NAFTA",
    ]

    remaining = df["CTY_NAME"].dropna().unique().tolist()

    still_bad = sorted(
        x for x in remaining
        if (x in forbidden_exact) or any(fragment in x for fragment in forbidden_fragments)
    )

    if still_bad:
        raise ValueError(
            f"Aggregate rows still remain after filtering: {still_bad}"
        )

    return df

def build_country_month_panel(imports: pd.DataFrame) -> pd.DataFrame:
    df = imports.copy()

    df = df.rename(columns={"CTY_NAME": "country", "GEN_VAL_MO": "import_value"})
    df["month"] = df["time"].dt.to_period("M").dt.to_timestamp()

    monthly_totals = (
        df.groupby("month", as_index=False)["import_value"]
        .sum()
        .rename(columns={"import_value": "total_import_value"})
    )

    df = df.merge(monthly_totals, on="month", how="left")
    df["country_share"] = df["import_value"] / df["total_import_value"]

    df = df.sort_values(["country", "month"]).reset_index(drop=True)

    df["country_share_ma3"] = (
        df.groupby("country")["country_share"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )

    df["share_volatility_12m"] = (
        df.groupby("country")["country_share"]
        .transform(lambda s: s.rolling(window=12, min_periods=6).std())
    )
    
    df["resilience_score"] = (
    (1 - df["country_share"]) /
    (df["share_volatility_12m"].fillna(0) + 0.0001)
    )

    return df


def build_concentration_metrics(panel: pd.DataFrame) -> pd.DataFrame:
    metrics = (
        panel.groupby("month")
        .agg(
            hhi=("country_share", lambda s: (s ** 2).sum()),
            c5_share=("country_share", lambda s: s.nlargest(5).sum()),
            supplier_count=("country_share", "size"),
        )
        .reset_index()
    )
    return metrics


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


def build_latest_exposure_table(panel: pd.DataFrame) -> pd.DataFrame:
    latest_month = panel["month"].max()
    latest = panel.loc[panel["month"] == latest_month].copy()

    latest = latest[
    [
        "month",
        "country",
        "import_value",
        "country_share",
        "country_share_ma3",
        "share_volatility_12m",
        "resilience_score"
    ]
    ].copy()

    latest["country_share_pct"] = latest["country_share"] * 100
    latest["country_share_ma3_pct"] = latest["country_share_ma3"] * 100
    latest["share_volatility_12m_pct"] = latest["share_volatility_12m"] * 100

    latest["resilience_score"] = latest["resilience_score"]

    latest = latest.sort_values("import_value", ascending=False).reset_index(drop=True)
    return latest


def main() -> None:
    print("Loading raw data...")
    imports, fred = load_raw_data()

    print("Filtering aggregate region rows...")
    imports = filter_aggregate_rows(imports)

    print("Building country-month panel...")
    panel = build_country_month_panel(imports)

    print("Calculating concentration metrics...")
    concentration = build_concentration_metrics(panel)

    print("Preparing FRED panel...")
    fred_panel = prepare_fred_panel(fred)

    print("Merging analytical dataset...")
    analytical = panel.merge(concentration, on="month", how="left")
    analytical = analytical.merge(fred_panel, on="month", how="left")
    analytical = analytical.sort_values(["month", "import_value"], ascending=[True, False])

    latest_exposure = build_latest_exposure_table(panel)

    panel.to_csv(PROCESSED_DIR / "country_month_panel.csv", index=False)
    concentration.to_csv(PROCESSED_DIR / "monthly_concentration_metrics.csv", index=False)
    analytical.to_csv(PROCESSED_DIR / "analytical_dataset.csv", index=False)
    latest_exposure.to_csv(PROCESSED_DIR / "latest_country_exposure.csv", index=False)

    print(f"Saved: {PROCESSED_DIR / 'country_month_panel.csv'}")
    print(f"Saved: {PROCESSED_DIR / 'monthly_concentration_metrics.csv'}")
    print(f"Saved: {PROCESSED_DIR / 'analytical_dataset.csv'}")
    print(f"Saved: {PROCESSED_DIR / 'latest_country_exposure.csv'}")

    print("\nTop 10 actual countries in latest month:")
    print(
    latest_exposure[
        [
            "country",
            "country_share_pct",
            "share_volatility_12m_pct",
            "resilience_score"
        ]
    ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()