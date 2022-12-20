import pandas as pd
import os
import difflib as dlb

base_dir = os.getcwd()

csvfl = "\\statements\\CapitalOne\\2022-11-09_transaction_download.csv"
csvflex = "\\statements\\CapitalOne\\2022-11-09_transaction_downloadex.csv"
csvsmp = "\\statements\\CapitalOne\\2022-11-09_Venture_bizFiltersmp.csv"


df_original =pd.read_csv(base_dir+csvfl)

df_auto = pd.read_csv(base_dir+csvflex)

# new descriptions/ categories dict
df_nw = pd.read_csv(base_dir+"\\descriptions.csv")

biz_sums = df_auto.groupby(['Subcat_1']).Debit.sum().reset_index()

catsums = df_auto.groupby(['Category']).Debit.sum().reset_index()


print(f"business cat sums: \n{biz_sums}\n**********\n")
print(f"std. category sums: \n{catsums}")
## putting the new desc. to the df_auto subcat2 column
# df_auto['Subcat_2'] = df_auto['Description'].map(lambda x: dlb.get_close_matches(x, df_nw['desc'], cutoff=0.2)[0] if len(dlb.get_close_matches(x, df_nw['desc'], cutoff=0.2)) > 1 else 'no match')
# df_auto['Subcat_2'] = 

# for idx, row in df_auto.iterrows():
#     # if "AVIS" in row.Description:
#     #     print('FUCKN A AVIS')
#     for ix, mrow in df_nw.iterrows():
#         if mrow.desc in row.Description:
#             print(f"match? {mrow}\n************\n{row}")

# newdsc = df_newdsc.to_dict(orient='records')
# df_newdsc.to_dict()

### so option
# df1['Category'] = 
#           df1['Description'].map(lambda x: difflib.get_close_matches(x, df2['item'], cutoff=0.3)[0] 
# cont.     if len(difflib.get_close_matches(x, df2['item'], cutoff=0.3)) > 1 else 'no match')

'''
df2:

item           category
mcdonald       fast food
state farm     insurance
break time     gas
chipotle       fast food
mobile         cell phone 
'''