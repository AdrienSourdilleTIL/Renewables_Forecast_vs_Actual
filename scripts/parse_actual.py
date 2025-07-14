import json
from pathlib import Path
from datetime import datetime, timedelta

def get_latest_actual_file(raw_dir):
    files = list(raw_dir.glob("actual_*.json"))
    if not files:
        raise FileNotFoundError("No actual files found.")
    
    def extract_date(f):
        try:
            return datetime.strptime(f.stem.split("_")[1], "%Y-%m-%d")
        except Exception:
            return datetime.min

    latest_file = max(files, key=extract_date)
    print(f"Latest actual file selected: {latest_file}")  # Debug print
    return latest_file

def extract_and_save_actual(data, production_type, output_dir):
    filtered_entries = [
        {
            'start_date': value['start_date'],
            'end_date': value['end_date'],
            'updated_date': value['updated_date'],
            'value': value['value'],
            'production_type': entry['production_type'],
        }
        for entry in data['actual_generations_per_production_type']
        if entry['production_type'] == production_type
        for value in entry['values']
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    output_file = output_dir / f"{production_type.lower()}_actual_{date_str}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_entries, f, ensure_ascii=False, indent=2)
    print(f"Saved {production_type} actual data to: {output_file}")  # Debug print

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent
    raw_dir = base_path / "data" / "Raw" / "Actual"

    latest_file = get_latest_actual_file(raw_dir)
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f'Loaded data from: {latest_file}')  # Debug print

    mapping = {
        'WIND_OFFSHORE': base_path / "data" / "Base" / "wind_offshore" / "actual",
        'WIND_ONSHORE': base_path / "data" / "Base" / "wind_onshore" / "actual",
        'SOLAR': base_path / "data" / "Base" / "solar" / "actual",
        # Add other production types as needed
    }

    for production_type, output_dir in mapping.items():
        extract_and_save_actual(data, production_type, output_dir)
