
img = 'recipts/rec1.jpg'
pdf = 'recipts/rec1.pdf'

from pdfminer.high_level import extract_text
text = extract_text(pdf)
print(text)