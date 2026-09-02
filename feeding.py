import csv
from datetime import datetime, timedelta
import io
import requests
from zoneinfo import ZoneInfo


SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMeg5CdW0iqiR7v53RbWWaZgmEMJlP6E1x0Hz9ySZU7gY269eqHgtgKsVgcemmB7hNfqjaWIw6Eh6E/pub?gid=505057465&single=true&output=csv"
EASTERN_TZ = ZoneInfo("America/New_York")


def get_daily_feeders():
    try:
        # Look up the next day in local time, since the sheet is for tomorrow's feeders.
        today = datetime.now(EASTERN_TZ)
        target_date = today + timedelta(days=1)
        target_month = target_date.month
        target_day = target_date.day

        # Fetch CSV data from Google Sheets
        response = requests.get(SHEET_CSV_URL, timeout=10)
        response.raise_for_status()

        # Parse CSV
        csv_file = io.StringIO(response.text)
        reader = csv.DictReader(csv_file)

        # Look for tomorrow's entry
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

            # Check for match with tomorrow's date
            if row_month == target_month and row_date == target_day:
                feeder1 = row.get("feeder1", "").strip()
                feeder2 = row.get("feeder2", "").strip()
                feeders = [name for name in (feeder1, feeder2) if name]

                if not feeders:
                    feeder_message = "Nobody is feeding tomorrow!!!"
                elif len(feeders) == 1:
                    feeder_message = f"{feeders[0]} and a ghost are feeding tomorrow! \n 👻"
                else:
                    feeder_message = f"{feeders[0]} and {feeders[1]} are feeding tomorrow!"

                return (
                    f"Feeding Reminder ({target_date.strftime('%B %d')}):\n\n"
                    f"{feeder_message}"
                )

        return f"Feeding Reminder ({target_date.strftime('%B %d')}):\nNo scheduled feeders found for tomorrow."

    except Exception as err:
        return f"Maddox I'm broken\n ({err})."


if __name__ == "__main__":
    print(get_daily_feeders())