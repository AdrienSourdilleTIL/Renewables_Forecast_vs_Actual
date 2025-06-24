import pandas as pd
from pathlib import Path

# Paths
data_folder = Path("C:/Users/AdrienSourdille/Renewables_Forecast_vs_Actual/data/CDM")
output_file = data_folder / "merged_forecast_actual.csv"

# Read and concatenate all daily CSV files
all_files = sorted(data_folder.glob("combined_forecast_actual_*.csv"))
df_list = [pd.read_csv(file) for file in all_files]
df = pd.concat(df_list, ignore_index=True)

# Save to CSV
df.to_csv(output_file, index=False)

print(f"Merged CSV saved to: {output_file}")
