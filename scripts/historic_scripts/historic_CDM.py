import json
from pathlib import Path
import pandas as pd
from datetime import datetime

def load_json_to_df(file_path, value_column_name):
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

        if not forecast_path.exists() or not actual_path.exists():
            return  # skip this date completely if anything is missing

        df_forecast = load_json_to_df(forecast_path, 'forecast_value')
        df_actual = load_json_to_df(actual_path, 'actual_value')

        df_merged = pd.merge(
            df_forecast,
            df_actual,
            on=['start_date', 'end_date', 'production_type'],
            how='outer'
        )
        combined_df_list.append(df_merged)

    if combined_df_list:
        combined_all = pd.concat(combined_df_list, ignore_index=True)
        combined_all = combined_all.sort_values(['production_type', 'start_date'])

        output_dir = base_path / "data" / "CDM"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"combined_forecast_actual_{date_str}.csv"
        combined_all.to_csv(output_file, index=False)
        print(f"[✓] {output_file.name}")
    else:
        print(f"[!] No combined data for {date_str}")

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent.parent
    sample_base = base_path / "data" / "Base" / "wind_onshore" / "forecast"

    # Get all unique dates from wind_onshore forecast files
    dates = sorted({f.stem.split('_')[-1] for f in sample_base.glob("*.json")})

    for date_str in dates:
        combine_forecast_actual(date_str, base_path)
