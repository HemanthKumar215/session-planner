# scheduler/backend/utils.py

import os
import PyPDF2
import re # Add this line
# import nltk # Uncomment if you install NLTK
# from nltk.corpus import stopwords # Uncomment if you install NLTK
# from nltk.tokenize import word_tokenize, sent_tokenize # Uncomment if you install NLTK

# Ensure NLTK data is downloaded if you use it (run this once)
# try:
#     nltk.data.find('punkt')
#     nltk.data.find('stopwords')
# except nltk.downloader.DownloadError:
#     nltk.download('punkt')
#     nltk.download('stopwords')


def extract_text_from_pdf(pdf_path):
    """
    Extracts text content from a PDF file.
    Args:
        pdf_path (str): The full path to the PDF file.
    Returns:
        str: The extracted text, or an empty string if an error occurs.
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() or ''
        return text
    except PyPDF2.errors.PdfReadError:
        print(f"Warning: Could not read PDF file {pdf_path}. It might be corrupted or encrypted.")
        return ""
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def preprocess_text(text):
    """
    Performs basic text preprocessing: lowercasing, removing non-alphanumeric, tokenization.
    This is a starting point; advanced NLP might require more sophisticated steps.
    Args:
        text (str): The raw text to preprocess.
    Returns:
        str: The preprocessed text.
    """
    # Lowercasing
    text = text.lower()
    # Remove non-alphanumeric characters (keep spaces)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Tokenization (if NLTK is used)
    # tokens = word_tokenize(text)
    # Remove stopwords (if NLTK is used)
    # stop_words = set(stopwords.words('english'))
    # filtered_tokens = [word for word in tokens if word not in stop_words]
    # return ' '.join(filtered_tokens)
    return text # Return raw text for now if NLTK is not used

def read_text_file(file_path):
    """
    Reads content from a plain text file.
    Args:
        file_path (str): The full path to the text file.
    Returns:
        str: The content of the file, or an empty string if an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading text file {file_path}: {e}")
        return ""
