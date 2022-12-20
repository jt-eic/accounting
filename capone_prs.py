import os
import tabula

import pdfminer

import camelot.io as camelot  ## to many stupid dependencies, pain in the ass. Try in another env for testing

stmt = "\\statements\\CapitalOne\\venture\\2019\\"

start_dir = os.getcwd()

onefile = "Statement_012019_7368.pdf"

testf = start_dir+stmt+onefile
print(testf)

# try tabula  ** is the winner for Capital One data... returns list
tabla = tabula.read_pdf(testf, pages='all', stream=True)
print(f"\nThis one is tabula: \n{tabla}")

'''
tables come in as mashed up dataframes. Need to organize them and format for export to csv 
as 
'''
## tried camelot. Maybe some other time, this one is a beast
# caml = camelot.read_pdf(testf, pages='all')

# print(f"this is the camelot version:\n {caml}\n*************")

