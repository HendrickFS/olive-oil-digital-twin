import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import os

# Create artifacts directory if not exists
artifact_dir = r"C:\Users\Hendrick\.gemini\antigravity\brain\64638ae7-4dd0-48c8-b6ae-66e5c1638aae"
os.makedirs(artifact_dir, exist_ok=True)

print("Loading dataset-3000.csv...")
df_3000 = pd.read_csv('api/ml/dataset-3000.csv')
synth_temp = df_3000['malaxationTemperature'].dropna()

print("Loading dataset-influx.csv...")
df_influx = pd.read_csv('api/ml/dataset-influx.csv')
df_influx['_time'] = pd.to_datetime(df_influx['_time'])

# Filter for mixers and temperature, and only keep data before Jan 1, 2026
df_influx_mixer = df_influx[
    (df_influx['thingId'].isin(['olive.production:mixer001', 'olive.production:mixer002'])) & 
    (df_influx['_field'] == 'temperature') &
    (df_influx['_time'] < pd.Timestamp('2026-01-01', tz='UTC'))
]
prod_temp = df_influx_mixer['_value'].dropna()

# Compute summary statistics
synth_stats = synth_temp.describe()
prod_stats = prod_temp.describe()

print("\n--- Synthetic Data Statistics (dataset-3000.csv) ---")
print(synth_stats)
print("\n--- Production Data Statistics (dataset-influx.csv, before Jan 2026) ---")
print(prod_stats)

# Perform statistical tests
# 1. Welch's t-test (tests if means are equal)
t_stat, p_val_t = stats.ttest_ind(synth_temp, prod_temp, equal_var=False)

# 2. Kolmogorov-Smirnov test (tests if distributions are the same)
ks_stat, p_val_ks = stats.ks_2samp(synth_temp, prod_temp)

print("\n--- Statistical Tests ---")
print(f"Welch's t-test: t-statistic = {t_stat:.4f}, p-value = {p_val_t:.4e}")
print(f"Kolmogorov-Smirnov test: KS-statistic = {ks_stat:.4f}, p-value = {p_val_ks:.4e}")

# Plot histograms
plt.figure(figsize=(10, 6))
plt.hist(prod_temp, bins=50, density=True, alpha=0.5, label='Production (Influx - Real)', color='blue')
plt.hist(synth_temp, bins=50, density=True, alpha=0.5, label='Synthetic (dataset-3000)', color='orange')
plt.title('Distribution of Malaxation Temperatures (Real Production Only)')
plt.xlabel('Temperature (°C)')
plt.ylabel('Density')
plt.legend()
plt.grid(True, alpha=0.3)

plot_path = os.path.join(artifact_dir, "temperature_distribution_filtered.png")
plt.savefig(plot_path)
print(f"\nPlot saved to {plot_path}")
