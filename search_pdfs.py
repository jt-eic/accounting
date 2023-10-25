import pandas as pd
from pdf_tools import *
from datetime import datetime


FILEDIR = "statements\\"
heads = ["file", "page", "value", "amount",]

searchtext = ["Lyft",
              "LYFT",
              "UBER",
            ]

mark_half = ['ATT', 'AT&T', 'COMCAST', ]

filesaved = "blank.csv"

divide_amount = .5


def makehalf(value):
    ''' change value to return .75% rather than half, as the phone and internet rate is higher than half'''
    return float(value)*.75


df = pd.read_csv(filesaved)

if __name__ == "__main__":
    starter = datetime.now()
    filelist = find_pdfs(FILEDIR)
    values = ""
    valulist = []

    for fl in filelist:
        with pdfplumber.open(fl) as pdffile:
            for pagenum in range(len(pdffile.pages)):

                pagetext = pdffile.pages[pagenum].extract_text()  # get it once, loop the list

                for txt in searchtext:
                    baseval = {}
                    values = find_value_by_text(pagetext, txt)
                    if values:
                        baseval['file'] = fl
                        baseval['page'] = pagenum
                        baseval.update(values)
                        baseval['date'] = split_datestr(fl)
                        valulist.append(baseval)

    for v in valulist:
        df = df.append(v, ignore_index=True)
    
    # do some new sorting and clean up: 
    df['deduction'] = df.apply(lambda row: makehalf(row['amount']) if row['text'] in mark_half else row['amount'], axis=1)

    df = df.sort_values(by='date', key=pd.to_datetime)

    ender = datetime.now()
    dur = ender - starter


    print(f"final dataframe:\n{df} \nThis took {dur} to complete {len(searchtext)} items.   ")





    if filesaved == 'blank.csv':
        filesaved = 'newfilename.csv'
    

    df.to_csv(filesaved, index=False)

