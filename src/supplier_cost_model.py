import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------
# Example sourcing benchmark inputs
# ---------------------------------------
# These are illustrative scenario inputs, not supplier quotes.
# The goal is to show procurement-style cost vs. risk tradeoffs.

data = {
    "country": ["Taiwan", "China", "Vietnam", "Mexico", "South Korea"],
    "unit_cost": [5.20, 5.10, 5.40, 5.90, 5.30],
    "shipping_cost": [0.80, 0.85, 0.75, 0.35, 0.80],
    "tariff_cost": [0.00, 0.40, 0.00, 0.00, 0.00],
    "risk_premium": [0.40, 0.30, 0.25, 0.15, 0.35],
}

df = pd.DataFrame(data)

# ---------------------------------------
# Compute total landed cost
# ---------------------------------------

df["total_landed_cost"] = (
    df["unit_cost"]
    + df["shipping_cost"]
    + df["tariff_cost"]
    + df["risk_premium"]
).round(2)

# ---------------------------------------
# Create a simple relative risk score
# ---------------------------------------
# We separate "risk premium" from a plotted "risk score"
# so the chart reads more clearly.
# Higher score = higher sourcing risk in this illustrative scenario.

risk_score_map = {
    "Mexico": 2.0,
    "Vietnam": 3.0,
    "China": 3.5,
    "South Korea": 4.0,
    "Taiwan": 4.5,
}

df["risk_score"] = df["country"].map(risk_score_map)

# ---------------------------------------
# Sort and save table
# ---------------------------------------

df = df.sort_values(["total_landed_cost", "risk_score"]).reset_index(drop=True)

print("\nSupplier Cost Comparison\n")
print(df)

df.to_csv("outputs/tables/supplier_cost_comparison.csv", index=False)

print("\nSaved table to outputs/tables/supplier_cost_comparison.csv")

# ---------------------------------------
# Cost vs risk tradeoff chart
# ---------------------------------------

plt.figure(figsize=(9, 6))
plt.scatter(df["risk_score"], df["total_landed_cost"], s=120)

for _, row in df.iterrows():
    plt.annotate(
        row["country"],
        (row["risk_score"], row["total_landed_cost"]),
        xytext=(6, 6),
        textcoords="offset points"
    )

plt.xlabel("Illustrative Sourcing Risk Score")
plt.ylabel("Total Landed Cost")
plt.title("Cost vs. Risk Tradeoff Across Illustrative Supplier Countries")
plt.grid(True, alpha=0.3)
plt.tight_layout()

chart_path = "outputs/charts/cost_vs_risk_tradeoff.png"
plt.savefig(chart_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved chart to {chart_path}")