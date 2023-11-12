import eel
import sqlite3
import os
import shutil
import atexit
import sys
import subprocess  # Required for calling the ocrmypdf command
import PyPDF2  # For reading PDFs

# Initialize Eel
eel.init('web')

# Get the directory of the current script
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)  # Executable directory
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Script directory

# Directories for storing PDFs
pdf_directory = os.path.join(script_dir, 'sample_pdfs')
pdf_result_directory = os.path.join(script_dir, 'web', 'sample_pdfs')
os.makedirs(pdf_result_directory, exist_ok=True)

def apply_ocr_to_pdf(input_path, output_path):
    try:
        subprocess.run(["ocrmypdf", "--skip-text", input_path, output_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running ocrmypdf: {e}")


def extract_text_from_pdf(file_path):
    text = ''
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + '\n'
    return text
# Function to process all PDFs in a directory
def process_pdf_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('.pdf'):
            input_path = os.path.join(directory_path, filename)
            output_path = os.path.join(directory_path, "ocr_" + filename)

            # Apply OCR and check if output file exists
            apply_ocr_to_pdf(input_path, output_path)
            if os.path.exists(output_path):
                # Extract text from the OCR-applied PDF
                content = extract_text_from_pdf(output_path)
                rel_path = os.path.relpath(output_path, directory_path)
                c.execute("INSERT INTO pdf_content (filename, content) VALUES (?, ?)", (rel_path, content))
                conn.commit()
            else:
                print(f"OCR output file not found for: {filename}")

# Check if database and table exist
def database_exists(db_path, table_name):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    exists = c.fetchone() is not None
    conn.close()
    return exists

# Clear previous search results from web folder
def clear_search_results(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Eel function to search PDF content and copy matching files
@eel.expose
def search_pdfs(keyword):
    trimmed_keyword = keyword.strip()
    print(f"Searching for: '{trimmed_keyword}'")
    try:
        search_query = "SELECT filename FROM pdf_content WHERE LOWER(content) LIKE LOWER(?)"
        c.execute(search_query, ('%' + trimmed_keyword + '%',))
        results = c.fetchall()

        # Clear previous search results
        clear_search_results(pdf_result_directory)

        # Copy matching PDFs to the web folder
        for result in results:
            original_file_path = os.path.join(pdf_directory, result[0])
            if os.path.exists(original_file_path):
                shutil.copy(original_file_path, pdf_result_directory)

        print(f"Found {len(results)} results for '{trimmed_keyword}'")
        return [os.path.join('sample_pdfs', os.path.basename(result[0])) for result in results]
    except Exception as e:
        print(f"Error during search: {e}")
        return []

# Main execution
if __name__ == '__main__':
    db_path = 'pdf_data.db'
    table_name = 'pdf_content'

    # Check and setup the database
    if not database_exists(db_path, table_name):
        print("Database does not exist. Creating and populating the database.")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE pdf_content (filename TEXT, content TEXT)''')
        process_pdf_directory(pdf_directory)
    else:
        print("Database already exists. Connecting to the existing database.")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

    atexit.register(lambda: conn.close())  # Ensure database connection is closed on exit
    print("Starting Eel application...")
    eel.start('main.html', size=(700, 700), mode='False')
