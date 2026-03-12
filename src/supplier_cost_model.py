import pandas as pd

# ---------------------------------------
# Example sourcing benchmark inputs
# ---------------------------------------

data = {
    "country": ["Taiwan", "China", "Vietnam", "Mexico", "South Korea"],
    
    # estimated component manufacturing cost
    "unit_cost": [5.20, 5.10, 5.40, 5.90, 5.30],
    
    # shipping cost to US manufacturing
    "shipping_cost": [0.80, 0.85, 0.75, 0.35, 0.80],
    
    # tariff assumptions
    "tariff_cost": [0.00, 0.40, 0.00, 0.00, 0.00],
    
    # simple risk premium derived from concentration exposure
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
)

# ---------------------------------------
# Sort by cheapest sourcing option
# ---------------------------------------

df = df.sort_values("total_landed_cost")

print("\nSupplier Cost Comparison\n")
print(df)

# ---------------------------------------
# Save results
# ---------------------------------------

df.to_csv(
    "outputs/tables/supplier_cost_comparison.csv",
    index=False
)

print("\nSaved results to outputs/tables/supplier_cost_comparison.csv")