import os
# import tabula
import camelot.io as camelot  ## to many stupid dependencies, pain in the ass. Try in another env for testing

stmt = "\\statements\\Chase\\BusinessChk\\2019\\"

start_dir = os.getcwd()

input_files = []  # collect ALL PDFs
for dirpath, subdirs, files in os.walk(start_dir+'\\statements\\Chase\\BusinessChk\\2019\\'):  # BusinessChk  PersonalChk
    for fl in files:
        if fl.endswith('.pdf'):
            fullfile = os.path.join(dirpath, fl)
            input_files.append(fullfile)

# pause = input("halt for a sec...")

# single for test
onefile = "20190131-statements-5281-.pdf"

testf = start_dir+stmt+onefile
print(testf)

# try tabula
# tabla = tabula.read_pdf(testf, pages='all')

## tried camelot. Maybe some other time, this one is a beast
caml = camelot.read_pdf(testf, flavor='stream')

