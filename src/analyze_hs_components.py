from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHART_DIR = BASE_DIR / "outputs" / "charts"
TABLE_DIR = BASE_DIR / "outputs" / "tables"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


AGGREGATE_NAMES = {
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
    "TOTAL FOR ALL COUNTRIES",
}


def filter_aggregate_rows(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["CTY_NAME"] = (
        out["CTY_NAME"]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    out = out.loc[~out["CTY_NAME"].isin(AGGREGATE_NAMES)].copy()
    return out


def build_hs_panel(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.rename(
        columns={
            "I_COMMODITY": "hs_code",
            "I_COMMODITY_SDESC": "hs_desc",
            "CTY_NAME": "country",
            "GEN_VAL_MO": "import_value",
            "GEN_QY1_MO": "import_qty",
            "UNIT_QY1": "qty_unit",
        }
    )

    out["month"] = pd.to_datetime(out["time"]).dt.to_period("M").dt.to_timestamp()

    monthly_totals = (
        out.groupby(["month", "hs_code"], as_index=False)["import_value"]
        .sum()
        .rename(columns={"import_value": "total_import_value"})
    )

    out = out.merge(monthly_totals, on=["month", "hs_code"], how="left")
    out["country_share"] = out["import_value"] / out["total_import_value"]

    # Unit value proxy when quantity exists
    out["unit_value_proxy"] = out["import_value"] / out["import_qty"]

    return out


def build_hs_concentration(panel: pd.DataFrame) -> pd.DataFrame:
    metrics = (
        panel.groupby(["month", "hs_code", "hs_desc"], as_index=False)
        .agg(
            hhi=("country_share", lambda s: (s ** 2).sum()),
            c3_share=("country_share", lambda s: s.nlargest(3).sum()),
            supplier_count=("country_share", "size"),
        )
    )
    return metrics


def latest_component_risk(concentration: pd.DataFrame) -> pd.DataFrame:
    latest_month = concentration["month"].max()
    latest = concentration.loc[concentration["month"] == latest_month].copy()

    latest["hhi_risk_band"] = pd.cut(
        latest["hhi"],
        bins=[-1, 0.15, 0.25, 1.0],
        labels=["Unconcentrated", "Moderately concentrated", "Highly concentrated"],
    )

    latest = latest.sort_values(["hhi", "c3_share"], ascending=[False, False])
    return latest


def build_latest_component_country_exposure(panel: pd.DataFrame) -> pd.DataFrame:
    latest_month = panel["month"].max()
    latest = panel.loc[panel["month"] == latest_month].copy()

    latest = latest[
        ["month", "hs_code", "hs_desc", "country", "import_value", "country_share"]
    ].copy()

    latest["country_share_pct"] = latest["country_share"] * 100
    latest = latest.sort_values(["hs_code", "country_share"], ascending=[True, False]).reset_index(drop=True)
    return latest


def build_component_supplier_summary(latest_exposure: pd.DataFrame, latest_risk: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []

    for hs_code, group in latest_exposure.groupby("hs_code"):
        group = group.sort_values("country_share", ascending=False).reset_index(drop=True)

        hs_desc = group.loc[0, "hs_desc"]

        top1_country = group.loc[0, "country"] if len(group) > 0 else None
        top1_share = group.loc[0, "country_share"] if len(group) > 0 else None

        top2_country = group.loc[1, "country"] if len(group) > 1 else None
        top2_share = group.loc[1, "country_share"] if len(group) > 1 else None

        top3_country = group.loc[2, "country"] if len(group) > 2 else None
        top3_share = group.loc[2, "country_share"] if len(group) > 2 else None

        top3_total = group["country_share"].head(3).sum()

        risk_row = latest_risk.loc[latest_risk["hs_code"] == hs_code].iloc[0]

        summary_rows.append(
            {
                "hs_code": hs_code,
                "hs_desc": hs_desc,
                "top1_country": top1_country,
                "top1_share_pct": top1_share * 100 if pd.notna(top1_share) else None,
                "top2_country": top2_country,
                "top2_share_pct": top2_share * 100 if pd.notna(top2_share) else None,
                "top3_country": top3_country,
                "top3_share_pct": top3_share * 100 if pd.notna(top3_share) else None,
                "top3_total_share_pct": top3_total * 100,
                "hhi": risk_row["hhi"],
                "c3_share_pct": risk_row["c3_share"] * 100,
                "supplier_count": risk_row["supplier_count"],
                "hhi_risk_band": risk_row["hhi_risk_band"],
            }
        )

    summary = pd.DataFrame(summary_rows)
    summary = summary.sort_values(["hhi", "top3_total_share_pct"], ascending=[False, False]).reset_index(drop=True)
    return summary


def chart_latest_hhi(latest: pd.DataFrame) -> None:
    plot_df = latest.sort_values("hhi", ascending=True).copy()

    plt.figure(figsize=(10, 6))
    labels = plot_df["hs_code"].astype(str) + " | " + plot_df["hs_desc"].astype(str)
    plt.barh(labels, plot_df["hhi"])
    plt.xlabel("HHI")
    plt.ylabel("HS6 Component")
    plt.title("Component-Level Sourcing Concentration (Latest Month)")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "hs_component_hhi_latest.png", dpi=300)
    plt.close()


def chart_latest_c3(latest: pd.DataFrame) -> None:
    plot_df = latest.sort_values("c3_share", ascending=True).copy()

    plt.figure(figsize=(10, 6))
    labels = plot_df["hs_code"].astype(str) + " | " + plot_df["hs_desc"].astype(str)
    plt.barh(labels, plot_df["c3_share"] * 100)
    plt.xlabel("Top-3 Country Share (%)")
    plt.ylabel("HS6 Component")
    plt.title("Top-3 Supplier Dependence by Component (Latest Month)")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "hs_component_c3_latest.png", dpi=300)
    plt.close()


def chart_top1_share(summary: pd.DataFrame) -> None:
    plot_df = summary.copy()

    short_desc_map = {
        "854232": "Memories ICs",
        "854231": "Processors / Controllers",
        "853400": "Printed Circuits",
        "854239": "Other ICs",
        "854233": "Amplifier ICs",
    }

    plot_df["short_component"] = plot_df["hs_code"].astype(str).map(short_desc_map).fillna(plot_df["hs_code"].astype(str))
    plot_df["component_label"] = plot_df["short_component"] + " | " + plot_df["top1_country"].astype(str)

    plot_df = plot_df.sort_values("top1_share_pct", ascending=True)

    plt.figure(figsize=(11, 6))
    bars = plt.barh(plot_df["component_label"], plot_df["top1_share_pct"])

    for bar, value in zip(bars, plot_df["top1_share_pct"]):
        plt.text(
            value + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}%",
            va="center"
        )

    plt.xlabel("Top Supplier Share (%)")
    plt.ylabel("Component | Dominant Supplier")
    plt.title("Dominant Supplier Country by Electronics Component")
    plt.xlim(0, max(plot_df["top1_share_pct"]) * 1.15)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "dominant_supplier_country_by_component.png", dpi=300)
    plt.close()


def main() -> None:
    df = pd.read_csv(RAW_DIR / "hs_component_imports.csv")

    print("Filtering aggregate rows...")
    df = filter_aggregate_rows(df)

    print("Building HS panel...")
    panel = build_hs_panel(df)

    print("Computing concentration metrics...")
    concentration = build_hs_concentration(panel)

    latest_risk = latest_component_risk(concentration)
    latest_exposure = build_latest_component_country_exposure(panel)
    supplier_summary = build_component_supplier_summary(latest_exposure, latest_risk)

    panel.to_csv(PROCESSED_DIR / "hs_component_panel.csv", index=False)
    concentration.to_csv(PROCESSED_DIR / "hs_component_concentration.csv", index=False)
    latest_risk.to_csv(TABLE_DIR / "hs_component_risk_latest.csv", index=False)
    latest_exposure.to_csv(TABLE_DIR / "hs_component_country_exposure_latest.csv", index=False)
    supplier_summary.to_csv(TABLE_DIR / "hs_component_supplier_summary_latest.csv", index=False)

    chart_latest_hhi(latest_risk)
    chart_latest_c3(latest_risk)
    chart_top1_share(supplier_summary)

    print(f"Saved: {PROCESSED_DIR / 'hs_component_panel.csv'}")
    print(f"Saved: {PROCESSED_DIR / 'hs_component_concentration.csv'}")
    print(f"Saved: {TABLE_DIR / 'hs_component_risk_latest.csv'}")
    print(f"Saved: {TABLE_DIR / 'hs_component_country_exposure_latest.csv'}")
    print(f"Saved: {TABLE_DIR / 'hs_component_supplier_summary_latest.csv'}")
    print(f"Saved: {CHART_DIR / 'hs_component_hhi_latest.png'}")
    print(f"Saved: {CHART_DIR / 'hs_component_c3_latest.png'}")
    print(f"Saved: {CHART_DIR / 'hs_component_top1_share_latest.png'}")

    print("\nLatest component risk ranking:")
    print(
        latest_risk[["hs_code", "hs_desc", "hhi", "c3_share", "supplier_count", "hhi_risk_band"]]
        .to_string(index=False)
    )

    print("\nLatest component supplier summary:")
    print(
        supplier_summary[
            [
                "hs_code",
                "top1_country",
                "top1_share_pct",
                "top2_country",
                "top2_share_pct",
                "top3_country",
                "top3_share_pct",
                "top3_total_share_pct",
                "hhi_risk_band",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()