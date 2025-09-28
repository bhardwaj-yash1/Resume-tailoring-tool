import fitz

def read_pdf(pdf_path:str)->str:
    doc=fitz.open(pdf_path)
    page=doc[0]
    content=page.get_text()
    return content
