import json
from pathlib import Path
from datetime import datetime

def get_latest_forecast_file(raw_dir):
    files = list(raw_dir.glob("forecast_*.json"))
    if not files:
        raise FileNotFoundError("No forecast files found.")
    
    # Extract date from filename and sort
    def extract_date(f):
        try:
            return datetime.strptime(f.stem.split("_")[1], "%Y-%m-%d")
        except Exception:
            return datetime.min

    latest_file = max(files, key=extract_date)
    return latest_file

def extract_and_save(data, production_type, output_dir):
    filtered_entries = [
        {
            'start_date': value['start_date'],
            'end_date': value['end_date'],
            'updated_date': value['updated_date'],
            'value': value['value'],
            'production_type': entry['production_type'],
        }
        for entry in data['forecasts']
        if entry['production_type'] == production_type
        for value in entry['values']
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_file = output_dir / f"{production_type.lower()}_forecast_{date_str}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_entries, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent
    raw_dir = base_path / "data" / "Raw" / "Forecast"

    latest_file = get_latest_forecast_file(raw_dir)
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f'latest_file: {latest_file}')

    mapping = {
        'WIND_OFFSHORE': base_path / "data" / "Base" / "wind_offshore" / "forecast",
        'WIND_ONSHORE': base_path / "data" / "Base" / "wind_onshore" / "forecast",
        'SOLAR': base_path / "data" / "Base" / "solar" / "forecast"
    }

    for production_type, output_dir in mapping.items():
        extract_and_save(data, production_type, output_dir)
