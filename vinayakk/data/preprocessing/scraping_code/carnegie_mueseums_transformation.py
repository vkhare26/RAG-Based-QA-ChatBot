import pandas as pd

def csv_to_paragraphs_txt(
    csv_file_path="/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/data/scraped_files/carnegie_museums_events_paragraphs.csv",
    txt_file_path="heinz_history_events.txt",
    title_col="title",
    desc_col="description"
):
    """
    Reads the CSV from 'csv_file_path', reorders columns so 'title' is first
    and 'description' is last (if they exist), then writes each row as a paragraph
    to 'txt_file_path'.
    """

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Identify all columns except 'title' and 'description'
    # (This helps us place 'title' first and 'description' last.)
    all_cols = list(df.columns)
    other_cols = [c for c in all_cols if c not in [title_col, desc_col]]

    # Build a new column order:
    #  1) title (if present)
    #  2) other columns
    #  3) description (if present)
    new_order = []
    if title_col in df.columns:
        new_order.append(title_col)
    new_order.extend(other_cols)
    if desc_col in df.columns:
        new_order.append(desc_col)

    # Reorder the DataFrame columns (only if they exist)
    # We'll intersect new_order with df.columns to avoid missing columns
    final_order = [col for col in new_order if col in df.columns]
    df = df[final_order]

    # Build paragraphs: each row => one paragraph with lines "ColumnName: value"
    paragraphs = []
    for _, row in df.iterrows():
        lines = [f"{col}: {row[col]}" for col in df.columns]
        paragraph = "\n".join(lines)
        paragraphs.append(paragraph)

    # Combine all paragraphs separated by two newlines
    output_text = "\n\n".join(paragraphs)

    # Save the output to a text file
    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"CSV '{csv_file_path}' has been converted to '{txt_file_path}' "
          f"with 'title' first and 'description' last if present.")


if __name__ == "__main__":
    csv_to_paragraphs_txt(
        csv_file_path="/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/data/scraped_files/carnegie_museums_events_paragraphs.csv",
        txt_file_path="heinz_history_events.txt",
        title_col="title",
        desc_col="description"
    )
