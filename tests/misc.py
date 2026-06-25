import os
import sys

# tests/inspect.py shadows the stdlib `inspect` that pdfminer imports; running a
# script in this dir puts it on sys.path[0]. Drop the script dir before importing
# pdfplumber. (centralia is installed, so it still imports fine.)
sys.path[:] = [
    p for p in sys.path if os.path.abspath(p or ".") != os.path.dirname(os.path.abspath(__file__))
]

import pdfplumber
from pprint import pprint
from pathlib import Path
filepath = "/Users/Palin/Code/centralia/assets/ca2/alvarenga_vides_v._blanche.pdf"


for fp in Path(filepath).parent.glob("*.pdf"):
    if "cruz_v" not in fp.name:
        continue
    with pdfplumber.open(fp) as pdf:
        page = pdf.pages[1]
        for page in pdf.pages[1:]:
            for word in page.extract_text_lines():
                print(word['text'].split()[0])

# okay. ca2 is the only one in the court of appeals that has some version of numbered lines... and its inconsistent yay. 

