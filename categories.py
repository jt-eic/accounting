import pandas as pd
import os

BASE_DIR = os.getcwd()
print(BASE_DIR)
WORKDIR = "\\statements\\CapitalOne\\venture\\2021"
trans_file = "\\statements\\FullYear_2021_capitalOne.csv"
fullfilepath = BASE_DIR + trans_file
data = pd.read_csv(fullfilepath)

print(data.columns)

# adding sub categories to another column by keywords
sub_cats = {
    'HILTON': 'Biz-travel',
    'MARRIOTT': 'Biz-travel',
    'LYFT': 'Biz-travel',
    'AVIS': 'Biz-travel',
    'DISNEYPLUS': 'streaming',
    'APPLE': 'biz-tech',
    'ROKU': 'streaming',
    'Roku': 'streaming',
    'DOUBLETREE': 'Biz-travel',
    'Prime Video': 'streaming',
    'ADAMS 12': 'education',
    'NETFLIX': 'streaming',
    'HULU': 'streaming',
    
    
}