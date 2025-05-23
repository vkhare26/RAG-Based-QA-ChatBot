import pandas as pd

# Read the CSV file generated by Selenium
csv_file_path = 'byham.csv'
df = pd.read_csv(csv_file_path)

# Function to ensure that the date string includes the year 2025
def add_year_to_date(date_str):
    if pd.isna(date_str):
        return date_str
    # If "2025" is not in the date, append ", 2025" to the date string.
    if "2025" not in date_str:
        return f"{date_str.strip()}, 2025"
    return date_str

# Update the "Date" column with the year 2025 if missing.
if "Date" in df.columns:
    df["Date"] = df["Date"].apply(add_year_to_date)
else:
    print("The CSV does not have a 'Date' column.")

# Build paragraphs: each row becomes a paragraph where each column is on its own line.
paragraphs = []
for index, row in df.iterrows():
    # Create a line for each column in the row.
    lines = [f"{col}: {row[col]}" for col in df.columns]
    # Join the lines with a newline character to form the paragraph.
    paragraph = "\n".join(lines)
    paragraphs.append(paragraph)

# Combine all paragraphs, separated by two newlines.
output_text = "\n\n".join(paragraphs)

# Save the output text to a file.
txt_file_path = 'byham.txt'
with open(txt_file_path, "w", encoding="utf-8") as f:
    f.write(output_text)

print("CSV has been converted to a text file with each row as a paragraph, and the Date column updated with 2025.")
