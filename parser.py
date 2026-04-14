import json


def extract_clean_text(source):
    """Extract clean page-marked text from LiteParse JSON output.

    Args:
        source: Either a file path (str) to a JSON file, or a dict already
                parsed from LiteParse JSON output.

    Returns:
        A tuple of (text, page_count).
    """
    if isinstance(source, dict):
        data = source
    else:
        print(f"Parsing {source}...")
        with open(source, 'r', encoding='utf-8') as file:
            data = json.load(file)

    pages = data.get('pages', [])
    full_text = ""

    for page in pages:
        page_num = page.get('page', 'Unknown')
        page_text = page.get('text', '')

        full_text += f"\n\n--- START OF PAGE {page_num} ---\n\n"
        full_text += page_text
        full_text += f"\n\n--- END OF PAGE {page_num} ---\n"

    return full_text, len(pages)

# Run the function
if __name__ == "__main__":
    # Point this to your uploaded file
    document_text, page_count = extract_clean_text("output_hsbc.md")

    # Save the clean output to a new text file for Ilira
    with open("clean_hsbc_report.txt", "w", encoding="utf-8") as out_file:
        out_file.write(document_text)
        
    print("Done! Clean text saved to clean_hsbc_report.txt")