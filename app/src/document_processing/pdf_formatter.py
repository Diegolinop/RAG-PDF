import re
import sys
from io import StringIO
from typing import Optional
import pdfplumber

class PDFFormatter:
    @staticmethod
    def extract_text(doc_path: str) -> Optional[str]:
        if not doc_path.endswith('.pdf'):
            raise ValueError('File must be a PDF')
            
        text_content = []
        try:
            with pdfplumber.open(doc_path) as pdf:
                for page in pdf.pages:
                    text_content.append(page.extract_text(x_tolerance=1, y_tolerance=1) or '')
            
            text = "\n".join(text_content)
            
            text = re.sub(r'journal homepage:.*?\n', '', text, flags=re.IGNORECASE)
            text = re.sub(r'^\s*Keywords:.*?\n', '', text, flags=re.MULTILINE | re.IGNORECASE)
            text = re.sub(r'^\s*Corresponding author:.*?\n', '', text, flags=re.MULTILINE | re.IGNORECASE)
            text = re.sub(r'\n\s*\n', '\n\n', text)
            return text.strip() if text else None
                                
        except Exception as e:
            raise RuntimeError(f'Failed to extract text from PDF: {str(e)}') from e

def read_file(path, output_filename='output.txt'):
    text = PDFFormatter.extract_text(path)
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(text or "")

def main():
    if len(sys.argv) < 2:
        print("Usage: python alternative.py <pdf-file> [output-file]")
        return
    input_path = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else 'output.txt'
    read_file(input_path, output_filename)

if __name__ == "__main__":
    main()