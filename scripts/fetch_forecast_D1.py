import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pathlib import Path
import json

load_dotenv()

TOKEN_URL = 'https://digital.iservices.rte-france.com/token/oauth/'
FORECAST_API_URL = 'https://digital.iservices.rte-france.com/open_api/generation_forecast/v2/forecasts'

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

def get_renewable_forecast(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    start_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=-1)
    end_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    params = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'type': 'D-1'
    }

    response = requests.get(FORECAST_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Forecast API request failed with status {response.status_code} - {response.text}")

if __name__ == "__main__":
    token = get_token()
    forecast_data = get_renewable_forecast(token)

    # One level above the script directory
    base_path = Path(__file__).resolve().parent.parent
    forecast_dir = base_path / "data" / "Raw" / "Forecast"
    forecast_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = forecast_dir / f"forecast_{date_str}.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(forecast_data, f, ensure_ascii=False, indent=2)