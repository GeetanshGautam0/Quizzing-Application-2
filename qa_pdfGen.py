from fpdf import FPDF

def createPDF(_d: list, _PdfN: str):
    pdf = FPDF()

    if not type(_d) is list: raise TypeError(f"Required type {list} for arg _d")
    if not type(_PdfN) is str: raise TypeError(f"Required type {str} for arg _PdfN")
    # Setup
    pdf.add_page()
    pdf.set_font("Courier", size=12)

    for x in _d:
        pdf.multi_cell(200, 5, txt=x, align='L')

    pdf.output(_PdfN)

def createStrPDF(_d: str, _fn: str):
    pdf = FPDF()

    pdf.add_page()
    pdf.set_font("Courier", size=12)

    pdf.cell(200, 10, txt=_d, ln=1, align="L")

    pdf.output(_fn)
