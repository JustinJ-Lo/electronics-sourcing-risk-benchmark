from pathlib import Path
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_TABLES = BASE_DIR / "outputs" / "tables"
OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

def main() -> None:
    df = pd.read_csv(PROCESSED_DIR / "hs_component_concentration.csv")
    feature_cols = [
        "hhi",
        "c3_share",
        "supplier_count",
    ]

    missing = [col for col in feature_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for clustering: {missing}")

    model_df = df.dropna(subset=feature_cols).copy()

    X = model_df[feature_cols].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    model_df["risk_cluster"] = kmeans.fit_predict(X_scaled)
    cluster_summary = (
        model_df.groupby("risk_cluster")[feature_cols]
        .mean()
        .round(4)
        .reset_index()
        .sort_values(["hhi", "c3_share"], ascending=[True, True])
        .reset_index(drop=True)
    )

    risk_label_map = {
        0: "lower concentration/broad supplier base",
        1: "elevated concentration",
        2: "lower concentration/moderate breadth",
        3: "highest concentration/dominant suppliers",
    }
    model_df["risk_cluster_label"] = model_df["risk_cluster"].map(risk_label_map)

    model_df.to_csv(PROCESSED_DIR / "hs_component_risk_clusters.csv", index=False)
    cluster_summary.to_csv(OUTPUT_TABLES / "risk_cluster_summary.csv", index=False)

    print("Saved clustered component outputs")
    print("\nColumns used:")
    for col in feature_cols:
        print(f"- {col}")

if __name__ == "__main__":
    main()