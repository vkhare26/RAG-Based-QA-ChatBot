import pandas as pd

# Read the CSV file into a DataFrame
csv_file_path = '/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/pittsburgh_opera_events.csv'
df = pd.read_csv(csv_file_path)

paragraphs = []

# Process each row: first column as title and last column as description.
for index, row in df.iterrows():
    # Use the first column for the title
    title = row[df.columns[0]]
    # Use the last column for the description
    description = row[df.columns[-1]]
    
    # Start with the title
    lines = [f"Title: {title}"]
    
    # Add any intermediate columns, if available
    for col in df.columns[1:-1]:
        lines.append(f"{col}: {row[col]}")
    
    # End with the description
    lines.append(f"Description: {description}")
    
    # Create the event paragraph
    paragraph = "\n".join(lines)
    paragraphs.append(paragraph)

# Combine all paragraphs separated by two newlines
output_text = "\n\n".join(paragraphs)

# Save the output to a text file
txt_file_path = '/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/pittsburgh_opera_events.txt'
with open(txt_file_path, "w", encoding="utf-8") as f:
    f.write(output_text)

print("CSV has been converted to a text file with each row as a paragraph, using the first column as the title and the last column as the description.")
