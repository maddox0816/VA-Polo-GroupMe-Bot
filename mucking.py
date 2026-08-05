import io
from datetime import datetime
import pandas as pd
import requests
from zoneinfo import ZoneInfo

# Direct Excel download URL
EXCEL_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_An-0FVaJaUdrkwfb55OVkhjBf7DyhEhcftCc1mw8ykse5ihndrNS3TAYNe1UAA08HjjuCzGlhtJk/pub?output=xlsx"
EASTERN_TZ = ZoneInfo("America/New_York")


def get_mucking_schedule():
    try:
        # 1. Fetch Excel file directly into memory
        response = requests.get(EXCEL_URL, timeout=15)
        response.raise_for_status()
        excel_bytes = io.BytesIO(response.content)

        # 2. Get today's local date details
        now = datetime.now(EASTERN_TZ)
        day_name = now.strftime("%A")  # e.g. "Monday", "Saturday"
        month_name = now.strftime("%B")  # e.g. "August", "September"
        day_num = now.day  # e.g. 15
        is_weekday = now.weekday() in {6, 0, 1, 3}  # Sun, Mon, Tues, Thurs

        muckers = []

        if is_weekday:
            # READ FROM "Weekly" TAB
            df_weekly = pd.read_excel(excel_bytes, sheet_name="Weekly")

            # Check if the weekday column exists in the tab
            matching_col = [
                col for col in df_weekly.columns if str(col).strip() == day_name
            ]
            if matching_col:
                col_data = df_weekly[matching_col[0]].dropna().tolist()
                # Clean entries and exclude header strings or instructions
                muckers = [
                    str(name).strip()
                    for name in col_data
                    if not str(name).startswith("^")
                    and "Varsity" not in str(name)
                ]

        else:
            # READ FROM MONTHLY TAB (e.g. "August", "September")
            xls = pd.ExcelFile(excel_bytes)
            if month_name in xls.sheet_names:
                df_month = pd.read_excel(excel_bytes, sheet_name=month_name)

                # Search grid for today's numerical date
                found = False
                for r_idx in range(len(df_month)):
                    for c_idx in range(7):
                        cell_val = df_month.iloc[r_idx, c_idx]
                        try:
                            if float(cell_val) == float(day_num):
                                # Look up to 5 rows below the date cell for signed-up names
                                for k in range(1, 6):
                                    if r_idx + k < len(df_month):
                                        name_val = df_month.iloc[
                                            r_idx + k, c_idx
                                        ]
                                        if pd.notna(name_val):
                                            try:
                                                # If it encounters another date or number, stop
                                                float(name_val)
                                                break
                                            except ValueError:
                                                muckers.append(
                                                    str(name_val).strip()
                                                )
                                found = True
                                break
                        except (ValueError, TypeError):
                            continue
                    if found:
                        break

        # 3. Format output string for GroupMe
        date_str = now.strftime("%B %d")
        if muckers:
            names_formatted = "\n".join([f"{name}" for name in muckers])
            return f"Mucking Reminder ({date_str}):\n\n{names_formatted}"
        else:
            return (
                f"Mucking Reminder ({date_str}):\nNobody is mucking today!!!\n\nWe need some volunteers!"
            )

    except Exception as err:
        return f"Maddox I'm broken\n ({err})."


if __name__ == "__main__":
    print(get_mucking_schedule())