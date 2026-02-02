"""
data_ingestion(Colab).py

Downloads ACLED data for Sudan (April 2019 - Present) using the ACLED API.
Designed to run in a Google Colab environment.

Outputs:
- beforeDDay.csv
"""

import os
import requests
import pandas as pd
from datetime import datetime
from google.colab import files
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
BEARER_TOKEN = os.getenv("ACLED_BEARER_TOKEN")
if BEARER_TOKEN is None:
    raise ValueError("ACLED_BEARER_TOKEN not found. Set it in Colab Secrets or os.environ.")

BASE_URL = "https://acleddata.com/api/acled/read"
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# Setup Retries
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
session.mount("https://", HTTPAdapter(max_retries=retries))

def download_data():
    """Download data pages from ACLED API."""
    all_data = []
    page = 1
    limit = 5000
    
    print(f"Starting download for Sudan: 2019-04-15 -> 2023-04-10")
    
    while True:
        params = {
            "country": "Sudan",
            "event_date": f"2023-04-11|2023-04-14",
            "event_date_where": "BETWEEN",
            "limit": limit,
            "page": page
        }
    
        try:
            response = session.get(BASE_URL, headers=HEADERS, params=params, timeout=60)
            response.raise_for_status()
            data_json = response.json()
    
            if data_json.get("status") != 200:
                print(f"API Error on page {page}: {data_json.get('messages')}")
                break
    
            batch = data_json.get("data", [])
            count = data_json.get("count", 0)
    
            if count == 0:
                print("No more data. Stopping.")
                break
    
            all_data.extend(batch)
            print(f"Page {page}: {count} rows")
    
            if count < limit:
                break
    
            page += 1
    
        except requests.exceptions.RequestException as e:
            print(f"Request failed on page {page}: {e}")
            break
            
    return all_data

if __name__ == "__main__":
    data = download_data()
    
    if not data:
        raise RuntimeError("No data retrieved. Check token or API limits.")
    
    df = pd.DataFrame(data)
    
    filename = "/content/beforeDDay.csv"
    df.to_csv(filename, index=False)
    
    print("\nSUCCESS")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    
    # Missing data report
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    
    print("\n--- Missing Data Report ---")
    print(missing if not missing.empty else "No missing values found.")
    
    # Auto-download to local machine
    try:
        files.download(filename)
    except Exception as e:
        print(f"Could not trigger browser download: {e}")

