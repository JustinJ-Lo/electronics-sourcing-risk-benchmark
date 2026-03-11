from pathlib import Path
from io import StringIO
import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

CENSUS_URL = (
    "https://api.census.gov/data/timeseries/intltrade/imports/naics"
    "?get=NAICS,CTY_CODE,CTY_NAME,GEN_VAL_MO"
    "&time=from+2021-01+to+2025-12"
    "&COMM_LVL=NA4"
    "&NAICS=3344"
)

FRED_SERIES = {
    "IZ3344": "import_price_index_overall",
    "COOASZ3344": "import_price_index_asian_nics",
    "COINDUSZ3344": "import_price_index_industrialized",
    "PCU33443344": "domestic_producer_price_index",
}


def fetch_census_imports() -> pd.DataFrame:
    response = requests.get(CENSUS_URL, timeout=30)
    response.raise_for_status()
    payload = response.json()

    df = pd.DataFrame(payload[1:], columns=payload[0])
    df["GEN_VAL_MO"] = pd.to_numeric(df["GEN_VAL_MO"], errors="coerce")
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    # Remove total row if present
    df = df[df["CTY_NAME"] != "TOTAL FOR ALL COUNTRIES"].copy()
    return df


def fetch_fred_csv(series_id: str, value_name: str) -> pd.DataFrame:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))
    df.columns = ["date", value_name]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df[value_name] = pd.to_numeric(df[value_name], errors="coerce")
    return df


def main() -> None:
    print("Fetching Census imports data...")
    imports_df = fetch_census_imports()
    imports_path = RAW_DIR / "census_imports_naics_3344.csv"
    imports_df.to_csv(imports_path, index=False)
    print(f"Saved: {imports_path}")

    fred_frames = []
    for series_id, value_name in FRED_SERIES.items():
        print(f"Fetching FRED series: {series_id}")
        fred_frames.append(fetch_fred_csv(series_id, value_name))

    fred_df = fred_frames[0]
    for frame in fred_frames[1:]:
        fred_df = fred_df.merge(frame, on="date", how="outer")

    fred_path = RAW_DIR / "fred_price_indexes_3344.csv"
    fred_df.to_csv(fred_path, index=False)
    print(f"Saved: {fred_path}")

    print("\nDone.")
    print(f"Census rows: {len(imports_df):,}")
    print(f"FRED rows:   {len(fred_df):,}")


if __name__ == "__main__":
    main()