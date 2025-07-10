import json
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

def load_json_to_df(file_path, value_column_name):
    print(f"Loading file: {file_path}")  # Debug
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df = df.rename(columns={'value': value_column_name})
    return df

def combine_forecast_actual(date_str, base_path):
    production_types = ['wind_offshore', 'wind_onshore', 'solar']
    combined_df_list = []

    for ptype in production_types:
        forecast_path = base_path / "data" / "Base" / ptype / "forecast" / f"{ptype}_forecast_{date_str}.json"
        actual_path = base_path / "data" / "Base" / ptype / "actual" / f"{ptype}_actual_{date_str}.json"

        print(f"\nChecking files for: {ptype}")
        print(f"  Forecast file: {forecast_path}")
        print(f"  Actual file:   {actual_path}")

        if not forecast_path.exists():
            print(f"  ❌ Forecast file missing: {forecast_path}")
        if not actual_path.exists():
            print(f"  ❌ Actual file missing: {actual_path}")

        if not forecast_path.exists() or not actual_path.exists():
            print(f"Skipping {ptype} due to missing files.")
            continue

        df_forecast = load_json_to_df(forecast_path, 'forecast_value')
        df_actual = load_json_to_df(actual_path, 'actual_value')

        df_merged = pd.merge(
            df_forecast,
            df_actual,
            on=['start_date', 'end_date', 'production_type'],
            how='outer'
        )
        combined_df_list.append(df_merged)
        print(f"  ✅ Merged data shape: {df_merged.shape}")

    if not combined_df_list:
        print("No data combined. Exiting.")
        return

    combined_all = pd.concat(combined_df_list, ignore_index=True)
    combined_all = combined_all.sort_values(['production_type', 'start_date'])

    output_dir = base_path / "data" / "CDM"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"combined_forecast_actual_{date_str}.csv"
    combined_all.to_csv(output_file, index=False)
    print(f"\n✅ Combined CSV saved to: {output_file}")

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent
    date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    combine_forecast_actual(date_str, base_path)
