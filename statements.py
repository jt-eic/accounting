import camelot
import pandas as pd
import os
from pdf_tools import find_pdfs


BASEDIR = os.getcwd()

SUB = "\\statements\\CapitalOne\\"

files = find_pdfs(BASEDIR+SUB)

print(files[5])

files22 = [x for x in files if "2022" in x]
flven = [x for x in files22 if "venture" in x]

usefile = flven[4]
test = camelot.read_pdf(usefile, flavor='stream')
print(test)
camelot.plot(test[0], kind='contour').show()

table = test[0].df

