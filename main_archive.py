import eel
import PyPDF2
import sqlite3
import os
import shutil
import atexit
import sys  # Import the sys module

# Initialize Eel
eel.init('web')

# Get the directory of the current script (works for both script and executable)
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)  # Get directory when run as executable
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get directory when run as script

# Directory for storing PDFs - original location (constructed relative path)
pdf_directory = os.path.join(script_dir, 'sample_pdfs')

# Directory for storing search result PDFs (inside the 'web' directory, constructed relative path)
pdf_result_directory = os.path.join(script_dir, 'web', 'sample_pdfs')

os.makedirs(pdf_result_directory, exist_ok=True)

# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

# Function to process all PDFs in a directory
def process_pdf_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory_path, filename)
            content = extract_text_from_pdf(file_path)
            # Store the relative path in the database
            rel_path = os.path.relpath(file_path, pdf_directory)
            c.execute("INSERT INTO pdf_content (filename, content) VALUES (?, ?)", (rel_path, content))
            conn.commit()

# Function to check if database and table exist
def database_exists(db_path, table_name):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    exists = c.fetchone() is not None
    conn.close()
    return exists

# Function to clear previous search results from web folder
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

# Run the Eel app
if __name__ == '__main__':
    db_path = 'pdf_data.db'
    table_name = 'pdf_content'

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
