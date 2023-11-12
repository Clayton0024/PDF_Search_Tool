# PDF Content Search Tool

## Description

This PDF Content Search Tool is a Python application designed to search for keywords within PDF documents. It uses OCR (Optical Character Recognition) to extract text from PDFs and stores the content in a SQLite database for efficient searching. The user interface is built using Eel, a simple web framework, allowing users to interact with the application through a web browser.

## Features

- **OCR Processing**: Converts image-based PDF content into searchable text.
- **SQLite Database**: Stores extracted text for quick searching.
- **Web Interface**: Easy-to-use interface for searching keywords within PDF documents.
- **Navigation Controls**: Browse through search results within the interface.
- **PDF Viewer**: Integrated PDF viewer to display the original documents.

## Requirements

- Python 3.x
- Eel (`pip install eel`)
- SQLite3 (included in standard Python library)
- PyPDF2 (`pip install PyPDF2`)
- OCRMyPDF (Install OCRMyPDF separately)
