import re
import sys
from PyPDF2 import PdfReader

def extract_is_numbers(pdf_path, output_path="bis_standards.txt"):
    is_pattern = re.compile(r'IS\s*\d+\s*:\s*\d{4}')
    reader = PdfReader(pdf_path)
    all_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"
    is_numbers = set(re.findall(is_pattern, all_text))
    with open(output_path, "w", encoding="utf-8") as f:
        for is_num in sorted(is_numbers):
            f.write(is_num.strip() + "\n")
    print(f"Extracted {len(is_numbers)} IS numbers to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_bis_numbers.py <path_to_pdf>")
    else:
        extract_is_numbers(sys.argv[1])
