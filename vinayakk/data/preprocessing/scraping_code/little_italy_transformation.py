import pandas as pd

# Read the CSV file into a DataFrame
csv_file_path = '/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/little_italy_days_schedule.csv'
df = pd.read_csv(csv_file_path)

paragraphs = []

# Determine the first and last column names
first_col = df.columns[0]
last_col = df.columns[-1]

# Process each row to build paragraphs
for index, row in df.iterrows():
    # Start with the title from the first column
    lines = [f"Title: {row[first_col]}"]
    
    # Add any intermediate columns with their column names
    for col in df.columns[1:-1]:
        lines.append(f"{col}: {row[col]}")
    
    # End with the description from the last column
    lines.append(f"Description: {row[last_col]}")
    
    # Combine the lines to form one paragraph for the event
    paragraph = "\n".join(lines)
    paragraphs.append(paragraph)

# Combine all event paragraphs separated by two newlines
output_text = "\n\n".join(paragraphs)

# Save the output to a text file
txt_file_path = '/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/little_italy_days_schedule.txt'
with open(txt_file_path, "w", encoding="utf-8") as f:
    f.write(output_text)

print("CSV has been converted to a text file with each row as a paragraph, where the first element is the title and the last element is the description.")
