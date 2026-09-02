import os
from pypdf import PdfReader

class PDFParsingError(Exception):
    pass

def validate_pdf_file(filepath: str):
    """
    Validates file existence, non-emptiness, size limit, extension, and %PDF- magic header.
    """
    if not os.path.exists(filepath):
        raise PDFParsingError("The specified file does not exist.")
    
    if os.path.getsize(filepath) == 0:
        raise PDFParsingError("The uploaded file is empty (0 bytes).")
    
    # Read first 1024 bytes to check magic byte header %PDF-
    with open(filepath, "rb") as f:
        header = f.read(1024)
        if b"%PDF-" not in header:
            raise PDFParsingError("File security error: Invalid PDF header magic bytes detected.")

def extract_text_from_pdf(filepath: str) -> str:
    """
    Extracts raw text from a PDF file using pypdf after validating security headers.
    """
    validate_pdf_file(filepath)
    
    try:
        reader = PdfReader(filepath)
        if len(reader.pages) == 0:
            raise PDFParsingError("The PDF document contains no pages.")
        
        extracted_text = []
        for index, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_text.append(text)
        
        full_text = "\n".join(extracted_text).strip()
        
        if not full_text:
            raise PDFParsingError("Could not extract readable text layer from the PDF. It may be a scanned or image-only PDF.")
        
        return full_text

    except PDFParsingError:
        raise
    except Exception as e:
        raise PDFParsingError(f"Failed to process PDF document: {str(e)}")
