import csv
from datetime import datetime, timedelta
import io
import requests
from zoneinfo import ZoneInfo


SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_An-0FVaJaUdrkwfb55OVkhjBf7DyhEhcftCc1mw8ykse5ihndrNS3TAYNe1UAA08HjjuCzGlhtJk/pub?gid=1248547830&single=true&output=csv"
EASTERN_TZ = ZoneInfo("America/New_York")



def get_daily_muckers():
    try:
        # Get today's date in local time
        today = datetime.now(EASTERN_TZ)
        target_month = today.month
        target_day = today.day 

        # Fetch CSV data from Google Sheets
        response = requests.get(SHEET_CSV_URL, timeout=10)
        response.raise_for_status()

        # Parse CSV
        csv_file = io.StringIO(response.text)
        reader = csv.DictReader(csv_file)

        # Look for today's entry
        for row in reader:
            raw_month = row.get("month", "").strip()
            raw_date = row.get("date", "").strip()

            # Skip rows where month or date are blank
            if not raw_month or not raw_date:
                continue

            try:
                row_month = int(raw_month)
                row_date = int(raw_date)
            except ValueError:
                continue
            
            # Check for match with today's date
            if row_month == target_month and row_date == target_day:
                # get muckers that will be in comma separated list like Gwen Darrow, Fernando Palacios, Samad Sultan (no car), Marcos (no car), Nora
                muckers_raw = row.get("muckers", "").strip()
                muckers = [name.strip() for name in muckers_raw.split(",") if name.strip()]

                if not muckers:
                    feeder_message = "Nobody is mucking today!!!"
                else:
                    feeder_message = f"{chr(10).join(muckers)} \nare mucking today!"

                return (
                    f"Mucking Reminder ({today.strftime('%B %d')}):\n\n"
                    f"{feeder_message}"
                )

        return f"Mucking Reminder ({today.strftime('%B %d')}):\nNo scheduled muckers found for today."

    except Exception as err:
        return f"Maddox I'm broken\n ({err})."


if __name__ == "__main__":
    print(get_daily_muckers())