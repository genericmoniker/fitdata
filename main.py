from datetime import datetime, timedelta
import json
from fitbit import get_spo2
from paths import FITBIT_CREDS, GOOGLE_AUTH
from sheets import add_spo2_to_sheet, open_sheet


def main():
    if not GOOGLE_AUTH.exists():
        print("Google authorized user file not found. Please run auth-main.py first.")
        exit(1)

    sheet = open_sheet("Fitdata")

    with FITBIT_CREDS.open() as creds_file:
        creds = json.load(creds_file)

    start = datetime(2024, 1, 1)
    yesterday = datetime.now() - timedelta(days=1)
    print(f"Retrieving SpO2 data from Fitbit for {yesterday.date()}...")
    data = get_spo2(creds, start, yesterday)
    print(f"Retrieved {len(data)} SpO2 record(s) from Fitbit.")

    # Save potentially updated credentials.
    with FITBIT_CREDS.open(mode="w") as creds_file:
        json.dump(creds, creds_file)

    print("Adding data to Google Sheet...")
    add_spo2_to_sheet(sheet, data)
    print("Data added successfully.")


if __name__ == "__main__":
    main()
