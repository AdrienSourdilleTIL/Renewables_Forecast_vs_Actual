import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pathlib import Path
import json

load_dotenv()

TOKEN_URL = 'https://digital.iservices.rte-france.com/token/oauth/'
ACTUAL_API_URL = 'https://digital.iservices.rte-france.com/open_api/actual_generation/v1/actual_generations_per_production_type'

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('SECRET_ID')

def get_token():
    response = requests.post(
        TOKEN_URL,
        data={'grant_type': 'client_credentials'},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"Token request failed with status {response.status_code}")

def get_actual_data_for_day(token, date):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    start_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=-1)
    end_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    params = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    }

    response = requests.get(ACTUAL_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed for {date.strftime('%Y-%m-%d')} - {response.status_code} - {response.text}")

if __name__ == "__main__":
    token = get_token()

    base_path = Path(__file__).resolve().parent.parent
    actual_dir = base_path / "data" / "Raw" / "Actual"
    actual_dir.mkdir(parents=True, exist_ok=True)

    current_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 6, 24)  # exclusive upper bound

    while current_date < end_date:
        try:
            print(f"Fetching data for {current_date.strftime('%Y-%m-%d')}")
            actual_data = get_actual_data_for_day(token, current_date)
            output_path = actual_dir / f"actual_{current_date.strftime('%Y-%m-%d')}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(actual_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error on {current_date.strftime('%Y-%m-%d')}: {e}")
        current_date += timedelta(days=1)
