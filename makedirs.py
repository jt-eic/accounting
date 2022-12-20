import os

BASEDIR = os.getcwd()
CARDDIRS = ["\\statements\\CapitalOne\\venture",
         "\\statements\\CapitalOne\\spark",
         ]

years = ['2018', '2019', '2020', '2021', '2022', '2023',]


for base in CARDDIRS:
    for yr in years:
        yrsl = f"\\{yr}\\"
        concat = BASEDIR+base+yrsl
        # newpath = os.path.join(concat, yrsl)
        os.mkdir(concat)
