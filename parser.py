import json

def extract_clean_text(file_path):
    print(f"Parsing {file_path}...")
    
    # 1. Load the JSON data (even though it ends in .md)
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    full_text = ""
    
    # 2. Loop through each page and extract the consolidated text
    for page in data.get('pages', []):
        page_num = page.get('page', 'Unknown')
        page_text = page.get('text', '')
        
        # 3. Format it cleanly for Ilira's LLM
        full_text += f"\n\n--- START OF PAGE {page_num} ---\n\n"
        full_text += page_text
        full_text += f"\n\n--- END OF PAGE {page_num} ---\n"
        
    return full_text

# Run the function
if __name__ == "__main__":
    # Point this to your uploaded file
    document_text = extract_clean_text("output_hsbc.md")
    
    # Save the clean output to a new text file for Ilira
    with open("clean_hsbc_report.txt", "w", encoding="utf-8") as out_file:
        out_file.write(document_text)
        
    print("Done! Clean text saved to clean_hsbc_report.txt")