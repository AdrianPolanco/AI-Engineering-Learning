from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(100, 10, txt="PDF generado desde Python", ln=True, align="C")
pdf.output("file.pdf")
