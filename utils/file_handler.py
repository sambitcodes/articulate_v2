"""
File handling utilities for articulAIte
"""

import streamlit as st
import PyPDF2
from docx import Document
from config import ALLOWED_FILE_TYPES, MAX_FILE_SIZE, ERROR_MESSAGES

def validate_file(uploaded_file):
    """Validate uploaded file"""
    if uploaded_file is None:
        return False, "No file selected"
    
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        return False, ERROR_MESSAGES["file_too_large"]
    
    # Check file type
    file_ext = uploaded_file.name.split('.')[-1].lower()
    if file_ext not in ALLOWED_FILE_TYPES:
        return False, ERROR_MESSAGES["invalid_file_type"]
    
    return True, "File valid"

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    try:
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return None

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file based on type"""
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    if file_ext == "pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_ext == "docx":
        return extract_text_from_docx(uploaded_file)
    elif file_ext == "txt":
        return uploaded_file.getvalue().decode("utf-8")
    
    return None
