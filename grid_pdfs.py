import camelot
import pandas as pd
import os
from pdf_tools import find_pdfs

''' Built this to gather grid/ spreadsheet from
show file documentation.

First glance at the file and find the page where
the show list is. Then append that page number in
front of the name: IE file name == "TorontoNHL.pdf
has the list on page 4, make it 4_TorontoNHL.pdf

This is written to take the page number from that front
of the name and use it to get only that page.

It will save the .csv file of that finding to the same
directory as the PDF is found.

'''


BASE_DIR = os.getcwd()
SUB = '\\SHOW_files\\'

files = find_pdfs(BASE_DIR+SUB)


def make_excel(thedata):
    '''once some data comes from the pdf, this formats it and makes
    it into an excel file'''
    for x in thedata:
        dataframe = x.df


def pull_showlist(file):
    ''' special fn. to get page num. from the filename, 
    then pull tables from that file and dump into a csv file'''
    parts = file.split('\\')
    page = parts[-1].split('_')[0]
    expname = parts[-1].replace('pdf', 'csv')
    print(f" file name: {expname} page num. {page}")
    try:
        data = camelot.read_pdf(file, pages=page, flavor='stream')
    except:
        data = camelot.read_pdf(file, pages=page)

    if not data:
        data = None
    return data, expname.replace(page, "")




if __name__ == "__main__":
    ## default flavor: lattice is default. stream is other option
    # one = camelot.read_pdf(files[5], pages=3)

    # test, fname = pull_showlist(files[2])
    
    for x in files:
        data, fname = pull_showlist(x)
        if data:
            data[0].df.to_csv(BASE_DIR+SUB+fname, index=False)
        else:
            continue

