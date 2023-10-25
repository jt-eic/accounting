import PyPDF2
import os
import pdfplumber
import re

def find_pdfs(directory):
    mylist = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                mylist.append(os.path.join(root, file))
    return mylist


def find_imgs(directory):
    mylist = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".jpg"):
                mylist.append(os.path.join(root, file))
                continue
            if file.lower().endswith(".png"):
                mylist.append(os.path.join(root, file))
    return mylist


def split_pdfs(inputpdf, outdir):
    with open(inputpdf, 'rb') as pdf_file:
        pdfreader = PyPDF2.PdfReader(pdf_file)
        pg_count = len(pdfreader.pages)
        if pg_count > 1:
            for pagenum in range(pg_count): 
                pdf_writer = PyPDF2.PdfWriter()
                pdf_writer.add_page(pdfreader.pages[pagenum])
                newfilepath = os.path.join(outdir, f'Page_{pagenum + 1}.pdf')
                with open(newfilepath, 'wb') as theFile:
                    pdf_writer.write(theFile)


def extract_text(file):
    ''' getting the text out of a pdf. ADD any methods in here and build conditions to eliminate
    the fluff, and just return a body of text it can use for the extraction of other stuff
    '''
    pdffile = pdfplumber.open(file)

    print(f" SOME GOD DAMN MESSAGE HERE... ")
    textdump = ""
    for i in pdffile.pages:
        print(i)
        foundtext = i.extract_text()
        textdump += foundtext

    return textdump



def find_text(file, search_text):
    '''detecting text within the PDF and returning the doc plus the page it was found on. For using reference to data
    on original documents. '''
    with pdfplumber.open(file) as pdffile:
        for page_num in range(len(pdffile.pages)):
            page = pdffile.pages[page_num]
            pg_text = page.extract_text()

            if search_text in pg_text:
                msg = f"file: {file} page: {page_num} contains: {search_text}"
            
    return msg


def split_datestr(value):
    '''takes 6 digit date like 092019 and returns it as 
    09-2019 for a date month/ year'''
    if "_" in value:
        pieces = value.split("_")[-2]
        return f"{pieces[:2]}/{pieces[-4:]}"
    else:
        endpart = value.split("\\")[-1]
        print(f" this date is {endpart}")

        return f"{endpart[4:6]}/{endpart[:4]}"


def find_value_by_text(pg_text, search_text):
    '''detecting text within the PDF and returning the doc, the page, and a numeric value after the text if available?'''
    rgx = fr'{re.escape(search_text)}.+[\d+.\d+]'

    altrgx = f"{search_text}.+[\d+.\d+]"
    results = {}

    if search_text in pg_text:
        rgline = re.findall(rgx, pg_text)
        try:
            dollarval = rgline[0].split('$')[1]
        except IndexError:
            dollarval = rgline[0].split()[-1]
        results = { 'text': search_text,
                    'amount': dollarval,
                    }

        if results:
            return results
        else:
            return None



if __name__ == '__main__':
    allfiles = ""
    print(f"running file locally.")
    
