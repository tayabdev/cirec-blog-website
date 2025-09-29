import PyPDF2
import os
import re
from werkzeug.utils import secure_filename
from flask import current_app

class PDFProcessor:
    
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """Extract full text content from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                page_count = len(pdf_reader.pages)
                
                for page_num in range(page_count):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
                
                # Clean up the extracted text
                cleaned_text = PDFProcessor.clean_extracted_text(text_content)
                
                return {
                    'full_text': cleaned_text,
                    'page_count': page_count,
                    'success': True
                }
        
        except Exception as e:
            return {
                'full_text': '',
                'page_count': 0,
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def clean_extracted_text(text):
        """Clean and normalize extracted text"""
        # Remove extra whitespaces and line breaks
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters and normalize
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def generate_preview_content(full_text, max_length=500):
        """Generate preview content from full text"""
        if not full_text:
            return ""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', full_text)
        
        preview = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(preview + sentence) < max_length:
                preview += sentence + ". "
            else:
                break
        
        return preview.strip()
    
    @staticmethod
    def save_uploaded_pdf(file, upload_folder):
        """Save uploaded PDF file securely"""
        try:
            # Create upload folder if it doesn't exist
            os.makedirs(upload_folder, exist_ok=True)
            
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Add timestamp to avoid conflicts
            import time
            timestamp = str(int(time.time()))
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            return {
                'success': True,
                'filename': unique_filename,
                'filepath': file_path,
                'filesize': file_size
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def validate_pdf_file(file):
        """Validate uploaded PDF file"""
        errors = []
        
        # Check if file is provided
        if not file or file.filename == '':
            errors.append('No file selected')
            return False, errors
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            errors.append('Only PDF files are allowed')
        
        # Check file size (50MB max)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
        if file_size > max_size:
            errors.append(f'File size too large. Maximum allowed: {max_size // (1024*1024)}MB')
        
        return len(errors) == 0, errors
    
    @staticmethod
    def extract_metadata_from_pdf(pdf_path):
        """Extract metadata from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                extracted_metadata = {}
                
                if metadata:
                    extracted_metadata['title'] = metadata.get('/Title', '')
                    extracted_metadata['author'] = metadata.get('/Author', '')
                    extracted_metadata['subject'] = metadata.get('/Subject', '')
                    extracted_metadata['creator'] = metadata.get('/Creator', '')
                    extracted_metadata['producer'] = metadata.get('/Producer', '')
                    extracted_metadata['creation_date'] = metadata.get('/CreationDate', '')
                
                return extracted_metadata
        
        except Exception as e:
            return {}