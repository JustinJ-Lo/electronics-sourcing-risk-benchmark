from pathlib import Path
import os
import requests
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

FRED_API_KEY = os.getenv("FRED_API_KEY")

FRED_SERIES = {
    "IZ3344": "import_price_index_overall",
    "COOASZ3344": "import_price_index_asian_nics",
    "COINDUSZ3344": "import_price_index_industrialized",
    "PCU33443344": "domestic_producer_price_index",
}

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch_fred_series(series_id: str, value_name: str) -> pd.DataFrame:
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
    }

    response = requests.get(FRED_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    observations = payload.get("observations", [])
    df = pd.DataFrame(observations)[["date", "value"]].copy()
    df = df.rename(columns={"value": value_name})

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df[value_name] = pd.to_numeric(df[value_name], errors="coerce")

    return df


def main() -> None:
    if not FRED_API_KEY:
        raise ValueError("Missing FRED_API_KEY environment variable.")

    frames = []
    for series_id, value_name in FRED_SERIES.items():
        print(f"Fetching {series_id}...")
        frames.append(fetch_fred_series(series_id, value_name))

    fred_df = frames[0]
    for frame in frames[1:]:
        fred_df = fred_df.merge(frame, on="date", how="outer")

    output_path = RAW_DIR / "fred_price_indexes_3344.csv"
    fred_df.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()