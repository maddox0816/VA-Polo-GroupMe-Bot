import csv
from datetime import datetime, timedelta
import io
import requests
from zoneinfo import ZoneInfo

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRDEBO6AR2B3lCJmKhhJKhx5OnCoMDCYbsmp8nAjGe-UaszRKtA65HhKXdRiOCy1sM3rbLWiTbIICGW/pub?gid=0&single=true&output=csv"
EASTERN_TZ = ZoneInfo("America/New_York")


def get_bootcamp_helpers():
    try:
        today = datetime.now(EASTERN_TZ)
        #set date to next day
        today = today.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        target_date_str = f"{today.month}/{today.day}"

        # 2. Fetch CSV data from Google Sheets
        response = requests.get(SHEET_CSV_URL, timeout=10)
        response.raise_for_status()

        # 3. Read and parse CSV
        csv_file = io.StringIO(response.text)
        reader = list(csv.reader(csv_file))

        helpers = []
        date_found = False

        for row in reader:
            if not row:
                continue

            # Check if the first cell matches today's date (e.g., "9/12")
            date_cell = row[0].strip()
            if date_cell == target_date_str:
                date_found = True
                # Collect helper names from the next columns (columns B, C, D, etc.)
                for cell in row[1:]:
                    cleaned_name = cell.strip()
                    # Skip empty cells or side notes/comments
                    if (
                        cleaned_name
                        and not cleaned_name.startswith("TOTAL")
                        and not cleaned_name.startswith("Everyone")
                        and not cleaned_name.startswith("36")
                        and not cleaned_name.startswith("**Fall")
                    ):
                        helpers.append(cleaned_name)
                break

        # 4. Format response message for GroupMe
        date_display = today.strftime("%B %d")

        if not date_found:
            raise Exception(f"No bootcamp session scheduled for {date_display}")

        if helpers:
            names_list = "\n".join([f"{name}" for name in helpers])
            return f"Bootcamp Reminder ({date_display}):\n{names_list}"
        else:
            return f"Bootcamp Reminder ({date_display}):\nNobody is signed up for bootcamp!!!\n\nWe need some volunteers!"

    except Exception as err:
        return f"Maddox I'm broken\n ({err})."


if __name__ == "__main__":
    print(get_bootcamp_helpers())