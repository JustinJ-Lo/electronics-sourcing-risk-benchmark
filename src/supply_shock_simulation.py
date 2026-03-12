import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# Load component-level supplier shares
df = pd.read_csv("data/processed/hs_component_panel.csv")

component = 854232  # memory ICs
shock_size = 0.5

# Filter to one component
component_df = df[df["hs_code"] == component].copy()

# Keep only latest month
latest_month = component_df["month"].max()
component_df = component_df[component_df["month"] == latest_month].copy()

# Apply shock
component_df["adjusted_share"] = component_df["country_share"]

taiwan_mask = component_df["country"].str.contains("taiwan", case=False, na=False)

if not taiwan_mask.any():
    raise ValueError("No Taiwan row matched in country column.")

component_df.loc[taiwan_mask, "adjusted_share"] *= (1 - shock_size)

# Compute supply after shock
total_supply_after_shock = component_df["adjusted_share"].sum()
supply_loss = 1 - total_supply_after_shock

print("Latest month:", latest_month)
print("Total supply after shock:", total_supply_after_shock)
print("Supply loss:", supply_loss)

# Save table
component_df[["country", "country_share", "adjusted_share"]].sort_values(
    "country_share", ascending=False
).to_csv("outputs/tables/taiwan_shock_memory_ics.csv", index=False)

# Plot
plot_df = pd.DataFrame({
    "scenario": ["Baseline", "Taiwan -50% Shock"],
    "available_supply": [1.0, total_supply_after_shock]
})

plt.figure(figsize=(8, 5))
bars = plt.bar(
    plot_df["scenario"],
    plot_df["available_supply"],
    color=["steelblue", "firebrick"]
)

plt.ylabel("Available Import Supply")
plt.title("Memory IC Supply Exposure Under Taiwan Shock")
plt.ylim(0, 1.05)
plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.02,
        f"{height:.1%}",
        ha="center"
    )

plt.savefig("outputs/charts/taiwan_shock_memory_ics.png", dpi=300, bbox_inches="tight")
plt.close()