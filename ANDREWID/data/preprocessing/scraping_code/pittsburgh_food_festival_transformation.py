import re
import pandas as pd

def transform_dates_and_drop_duplicates(input_csv, output_csv):
    """
    Reads the events CSV from 'input_csv', modifies the 'date_range' column
    by appending '2025' if the month is Mar-Dec, otherwise '2026' if Jan-Feb,
    then drops duplicates based on (title, date_range, venue),
    and saves the result to 'output_csv'.
    """
    df = pd.read_csv(input_csv)

    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    def append_year_to_date_range(date_text: str) -> str:
        if not isinstance(date_text, str) or date_text == "N/A":
            return date_text
        match = re.match(r"([A-Za-z]{3})", date_text)
        if match:
            abbrev = match.group(1).capitalize()
            if abbrev in month_map:
                month_num = month_map[abbrev]
                year = 2025 if month_num >= 3 else 2026
                return f"{date_text}, {year}"
        return date_text

    if "date_range" in df.columns:
        df["date_range"] = df["date_range"].apply(append_year_to_date_range)
    else:
        print("Warning: 'date_range' column not found in the input CSV.")

    subset_cols = ["title", "date_range", "venue"]
    for col in subset_cols:
        if col not in df.columns:
            print(f"Warning: '{col}' column not found in the input CSV. Duplicates may not be removed correctly.")

    df.drop_duplicates(subset=subset_cols, inplace=True)
    df.to_csv(output_csv, index=False)
    print(f"Transformed data saved to '{output_csv}'.")

if __name__ == "__main__":
    input_file = "visit_pittsburgh_events_pages1to5.csv"
    output_file = "visit_pittsburgh_events_pages1to5_withyear.csv"
    transform_dates_and_drop_duplicates(input_file, output_file)
