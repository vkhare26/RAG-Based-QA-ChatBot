import pandas as pd

# Read the CSV file into a DataFrame
csv_file_path = '/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/heinz_history_events.csv'
df = pd.read_csv(csv_file_path)

paragraphs = []

# Get the first and last column names
first_col = df.columns[0]
last_col = df.columns[-1]

for index, row in df.iterrows():
    # Start the paragraph with the title (first element)
    lines = [f"Title: {row[first_col]}"]
    
    # Add any intermediate columns, if they exist
    for col in df.columns[1:-1]:
        lines.append(f"{col}: {row[col]}")
    
    # End the paragraph with the description (last element)
    lines.append(f"Description: {row[last_col]}")
    
    # Join all lines into one paragraph
    paragraph = "\n".join(lines)
    paragraphs.append(paragraph)

# Combine all paragraphs with two newlines between them
output_text = "\n\n".join(paragraphs)

# Save the output to a text file
txt_file_path = '/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/heinz_history_events.txt'
with open(txt_file_path, "w", encoding="utf-8") as f:
    f.write(output_text)

print("CSV has been converted to a text file with each row as a paragraph where the first element is the title and the last element is the description.")
