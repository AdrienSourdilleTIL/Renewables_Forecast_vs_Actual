import json
from pathlib import Path
from datetime import datetime

def extract_and_save_actual(data, production_type, output_dir, date_str):
    filtered_entries = [
        {
            'start_date': value['start_date'],
            'end_date': value['end_date'],
            'updated_date': value['updated_date'],
            'value': value['value'],
            'production_type': entry['production_type'],
        }
        for entry in data.get('actual_generations_per_production_type', [])
        if entry['production_type'] == production_type
        for value in entry['values']
    ]

    if filtered_entries:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{production_type.lower()}_actual_{date_str}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_entries, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent.parent
    raw_dir = base_path / "data" / "Raw" / "Actual"

    mapping = {
        'WIND_OFFSHORE': base_path / "data" / "Base" / "wind_offshore" / "actual",
        'WIND_ONSHORE': base_path / "data" / "Base" / "wind_onshore" / "actual",
        'SOLAR': base_path / "data" / "Base" / "solar" / "actual",
        # Add other production types if needed
    }

    for json_file in sorted(raw_dir.glob("actual_*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            date_str = json_file.stem.split("_")[1]
            print(f"Parsing file: {json_file.name}")
            for production_type, output_dir in mapping.items():
                extract_and_save_actual(data, production_type, output_dir, date_str)
        except Exception as e:
            print(f"Error parsing {json_file.name}: {e}")
