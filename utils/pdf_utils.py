import fitz

def read_pdf(pdf_path:str)->str:
    doc=fitz.open(pdf_path)
    page=doc[0]
    content=page.get_text()
    return content


def save_latex_code(latex:str,save_path:str):
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(latex)