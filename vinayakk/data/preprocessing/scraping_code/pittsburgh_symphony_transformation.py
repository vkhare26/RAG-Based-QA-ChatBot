import pandas as pd

# Read the CSV file into a DataFrame
csv_file_path = '/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/pso_events_about.csv'
df = pd.read_csv(csv_file_path)

# Define the columns to exclude from the output
exclude_cols = ['number', 'date_attr']

# Build a list of columns that will be included (i.e. exclude the ones defined above)
included_columns = [col for col in df.columns if col not in exclude_cols]

# Ensure there are at least two columns after exclusion for title and description.
if len(included_columns) < 2:
    raise ValueError("Not enough columns remaining for title and description after excluding 'number' and 'date_attr'.")

paragraphs = []

# Process each row to create a paragraph for each event.
for index, row in df.iterrows():
    # Use the first column in the filtered list as the title,
    # and the last column as the description.
    title = row[included_columns[0]]
    description = row[included_columns[-1]]
    
    lines = [f"Title: {title}"]
    
    # Add the intermediate columns (if any) with their values.
    for col in included_columns[1:-1]:
        lines.append(f"{col}: {row[col]}")
    
    lines.append(f"Description: {description}")
    
    # Join the lines to form a paragraph.
    paragraph = "\n".join(lines)
    paragraphs.append(paragraph)

# Combine all paragraphs with two newlines in between.
output_text = "\n\n".join(paragraphs)

# Save the resulting text to a .txt file
txt_file_path = '/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/pso_events_about.txt'
with open(txt_file_path, "w", encoding="utf-8") as f:
    f.write(output_text)

print("CSV has been converted to a text file with each row as a paragraph, excluding 'number' and 'date_attr' columns.")
