import fitz
import subprocess
import os

def read_pdf(pdf_path:str)->str:
    doc=fitz.open(pdf_path)
    page=doc[0]
    content=page.get_text()
    return content


def save_latex_code(latex:str,save_path:str):
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(latex)


def latex_to_pdf(latex_file_path: str):

    directory=os.path.dirname(latex_file_path)
    filename=os.path.basename(latex_file_path)

    if directory=='':
        directory='.'

     
    commands=['pdflatex','-interaction=nonstopmode',f'-output-directory={directory}',filename]

    for i in range(2):

        try:
            result=subprocess.run(
            commands,   
            cwd=directory,
            capture_output=True,
            text=True,
            check=True)

        except FileNotFoundError:
            print("❌ Error: 'pdflatex' command not found.")
            print("Please ensure you have a LaTeX distribution (like MiKTeX, TeX Live) installed and in your system's PATH.")
            return None
        
        except subprocess.CalledProcessError as e:
            # This block catches errors from the pdflatex compilation itself.
            print(f"❌ LaTeX compilation failed on pass {i + 1}.")
            print("----------------- LaTeX Error Log -----------------")
            # The error log from LaTeX is the most useful part for debugging.
            print(e.stdout)
            print("---------------------------------------------------")
            return None
        
    pdf_filename=os.path.splitext(filename)[0]+'.pdf'
    pdf_path=os.path.join(directory,pdf_filename)

    if os.path.exists(pdf_path):
           print(f"✅ Successfully created PDF: '{pdf_path}'")
           return pdf_path
    else:
           print("❌ Error: PDF file was not generated, even though compilation reported success.")
           return None
        
