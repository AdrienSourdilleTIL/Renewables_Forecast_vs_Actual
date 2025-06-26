import json
from pathlib import Path
import pandas as pd
from datetime import datetime

def load_json_to_df(file_path, value_column_name):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # data is a list of dicts with keys including start_date, end_date, production_type, value
    df = pd.DataFrame(data)
    df = df.rename(columns={'value': value_column_name})
    return df

def combine_forecast_actual(date_str, base_path):
    # Define production types and paths
    production_types = ['wind_offshore', 'wind_onshore', 'solar']  # add more if needed

    combined_df_list = []

    for ptype in production_types:
        forecast_path = base_path / "data" / "Base" / ptype / "forecast" / f"{ptype}_forecast_{date_str}.json"
        actual_path = base_path / "data" / "Base" / ptype / "actual" / f"{ptype}_actual_{date_str}.json"

        if not forecast_path.exists() or not actual_path.exists():
            print(f"Missing files for {ptype} on {date_str}, skipping...")
            continue

        df_forecast = load_json_to_df(forecast_path, 'forecast_value')
        df_actual = load_json_to_df(actual_path, 'actual_value')

        # Merge on start_date, end_date, production_type
        df_merged = pd.merge(
            df_forecast,
            df_actual,
            on=['start_date', 'end_date', 'production_type'],
            how='outer'
        )
        combined_df_list.append(df_merged)

    if not combined_df_list:
        print("No data to combine for this date.")
        return

    combined_all = pd.concat(combined_df_list, ignore_index=True)

    # Sort by production_type and start_date
    combined_all = combined_all.sort_values(['production_type', 'start_date'])

    # Save combined CSV
    output_dir = base_path / "data" / "CDM"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"combined_forecast_actual_2025-06-24.csv"
    combined_all.to_csv(output_file, index=False)
    print(f"Combined file saved to {output_file}")

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent
    date_str = datetime.now().strftime("%Y-%m-%d")  # or set any date you want here

    combine_forecast_actual(date_str, base_path)
