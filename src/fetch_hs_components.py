from pathlib import Path
from io import StringIO
import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

HS_CODES = [
    "854231",  # processors/controllers
    "854232",  # memories
    "854233",  # amplifiers
    "854239",  # other integrated circuits
    "853400",  # printed circuits
]

BASE_URL = "https://api.census.gov/data/timeseries/intltrade/imports/hs"


def fetch_one_hs_code(hs_code: str) -> pd.DataFrame:
    """
    Pull monthly U.S. imports by country for one HS6 code.
    """
    url = (
        f"{BASE_URL}"
        f"?get=I_COMMODITY,I_COMMODITY_SDESC,CTY_CODE,CTY_NAME,GEN_VAL_MO,GEN_QY1_MO,UNIT_QY1,COMM_LVL"
        f"&time=from+2021-01+to+2025-12"
        f"&COMM_LVL=HS6"
        f"&I_COMMODITY={hs_code}"
    )

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    payload = response.json()
    df = pd.DataFrame(payload[1:], columns=payload[0])

    df["GEN_VAL_MO"] = pd.to_numeric(df["GEN_VAL_MO"], errors="coerce")
    df["GEN_QY1_MO"] = pd.to_numeric(df["GEN_QY1_MO"], errors="coerce")
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    return df


def main() -> None:
    frames = []

    for hs_code in HS_CODES:
        print(f"Fetching HS6 code: {hs_code}")
        df = fetch_one_hs_code(hs_code)
        frames.append(df)

    hs_df = pd.concat(frames, ignore_index=True)

    output_path = RAW_DIR / "hs_component_imports.csv"
    hs_df.to_csv(output_path, index=False)

    print(f"\nSaved: {output_path}")
    print(f"Rows: {len(hs_df):,}")

    hs_codes_found = (
        pd.Series(hs_df["I_COMMODITY"].to_numpy().ravel())
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    print(f"HS codes: {sorted(hs_codes_found)}")

if __name__ == "__main__":
    main()