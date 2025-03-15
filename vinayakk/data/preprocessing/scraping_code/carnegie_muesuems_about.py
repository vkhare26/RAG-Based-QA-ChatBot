import pandas as pd

# Read the CSV file into a DataFrame
csv_file_path = '/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/carnegie_about.csv'
df = pd.read_csv(csv_file_path)

paragraphs = []

# Ensure there are at least two columns (Title and Full Text)
if len(df.columns) < 2:
    raise ValueError("CSV file must have at least two columns (Title and Full Text)")

# Process each row: use first column as Title.
# If the CSV has three or more columns, assume:
#   - The second column is the summary,
#   - The last column is the full text.
# For CSVs with exactly two columns, treat the second column as full text.
for index, row in df.iterrows():
    title = row[df.columns[0]]
    if len(df.columns) >= 3:
        summary = row[df.columns[1]]
        full_text = row[df.columns[-1]]
    else:
        summary = ""
        full_text = row[df.columns[1]]
    
    # Build the event paragraph:
    # The title is on its own line, followed by a blank line,
    # then a paragraph that combines summary and full text.
    if summary:
        combined_info = f"Summary: {summary} Full Text: {full_text}"
    else:
        combined_info = f"Full Text: {full_text}"
    
    event_paragraph = f"Title: {title}\n\n{combined_info}"
    paragraphs.append(event_paragraph)

# Combine all event paragraphs separated by two newlines
output_text = "\n\n".join(paragraphs)

# Save the output to a text file
txt_file_path = '//Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/carnegie_about.txt'
with open(txt_file_path, "w", encoding="utf-8") as f:
    f.write(output_text)

print("CSV has been converted to a text file where each event is formatted as a paragraph containing the title, summary, and full text.")
