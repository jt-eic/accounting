import veryfi
from veryfi import VeryfiClientError
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import parsedatetime as pdt
import pandas as pd
import pickle
from build_invoice import day_and_month  # makes it cool like Mon. Feb. 22 or whatever
from pull_lyft import parse_ride

## basics to start:  
std_customer = "Mobile TV Group"

# jobs = pd.read_csv("newinv_2022-11-26.csv")  # redo and get jobs from portal or create this from invoice runner

# make a useful dict for date matches
with open("workorders.pkl", 'rb') as pklfile:
    wk_dates = pickle.load(pklfile)


''' using the veryfi system try to integrate this instead of my other parser. MORE accurate? SO FAR, YES'''
###  ******************************************************    Loading for veryfi  ****************
load_dotenv()

client_id = os.environ.get('VFY_ID')
client_secret = os.environ.get('VFY_SEC')
client_user = os.environ.get('VFY_USNAME')
apikey = os.environ.get('VFY_APIKEY')

client = veryfi.Client(client_id, client_secret, client_user, apikey)

categories = ['Travel Expense', 'Lodging', 'Truck supplies',]  # not much, but I can add eventually

### *********************************************************  Some tools for dates and stuff  
cal = pdt.Calendar()
def get_dates(datestr: str): 
    """takes any format date through parsedatetime and output back a before and after date to get matches"""
    try:
        parsed = cal.parseDT(datestr)[0]
    except ValueError:
        parsed = cal.parseDateText(datestr)[0]
    except AttributeError:
        parts = cal.parse(datestr)[0]  # makes a tuple of time.struct_time
        newstr = f"{parts.tm_year}-{parts.tm_mon}-{parts.tm_mday}"
        parsed = cal.parseDate(newstr)
    
    prev = parsed - timedelta(days=1)
    next = parsed + timedelta(days=1)


    return prev, parsed, next


def fmt_date(datestr: str):
    """take in the date object and quickly make it as mm/dd/yyyy for matching"""
    return datetime.strftime(datestr, "%m/%d/%Y")


def make_day_mo(dateobj):
    ''' uses any date from get_dates and spits back out as ex: Sun Feb. 19 type date'''
    return datetime.strftime(dateobj, "%a %b. %d")

### ******************************************************************************************


## try each of these files: get ALL
exp_dir = "current expenses\\"
allfiles = os.listdir(exp_dir)

parseddata = []
ext_file = "expenses_parsed.pkl"

# with open(ext_file, 'rb') as expload:
#     parseddata.load(expload)

###### this section here for the real deal. Do reload data from pickle file for building...
parsecount = 0  
if __name__ == '__main__':

    for idx, file in enumerate(allfiles):
        print(file)

        if 'csv' in file:  # currently only LYFT files have csv; get it as iterable
            lyftdf = pd.read_csv(exp_dir+file)
            lyftrides = lyftdf.to_dict('records')
            for ride in lyftrides:
                rslt = parse_ride(ride)  # This matches the fields like above
                # continue  # maybe put csv parser later.. or first?
                vendor = "Lyft"
                paid_thr = 2104  # CC last 4 on all LYFT rides
                expdate = rslt['ridedate'] #comes from the parse_ride, figured out by ride details
                yst, exp_date, tommo = get_dates(expdate[:10])  # redundant? use of 'today' vs. expdate may be 
                print(f" dates: from expense: {expdate} and the get_Dates {exp_date}")
                wonum = wk_dates[fmt_date(rslt['jdate'])]
                # these fields again, per line in the CSV. Did separately and it only added ONE single expense from the whole .csv file
                account = rslt['category']  # for which expense category/ expense account in books
                amount = rslt['total']
                notes = rslt['purpose']
                details = f"{account} {vendor}"    # add more here from specific details like lyft ride info or whatever
                desc_string = f"{details}: {notes}"

                parsedline = {
                    'Expense Date': expdate[:10], 
                    'Expense Description': f"{desc_string}\n{make_day_mo(exp_date)}, WO#{wonum}",   # stack up some other data and fill in this one; 
                    'Expense Account':account, 
                    'Paid Through':paid_thr, 
                    'Vendor':vendor, 
                    'Expense Amount':amount, 
                    'Reference#': wonum, 
                    'Is Billable':True, 
                    'Customer Name':std_customer, 
                    'Is Reimbursable':True,
                    }
                parseddata.append(parsedline)
                
            # at this level, do the PDF rename step for the matching PDF ride report
            # namedate = today.isoformat()[:10]
            pdfname = file.replace('.csv', '.pdf')  # for renaming the matching pdf later
            newname = f"{wonum}_{vendor}_{expdate[:10]}.pdf"  # only need VENDOR for lyft, its short.
            os.rename(exp_dir+pdfname, exp_dir+newname)

            # now which ever it is PDF or CSV, rename the pdf for it:
            print(f" the renamed filename: {newname}")

        ## This level: PDFs or .PNG...   make sure rename works specific for each!
        else:
            if "ride_report" in file:
                # this is the PDF for lyft, skip it but still rename the pdf.. job_
                continue
            try:
                rslt = client.process_document(exp_dir+file, categories)  # all the magic in here...     : )
                parsecount += 1
            except VeryfiClientError:
                print(f" exceeded amount: skip PDFs for now.")
                continue
            expdate = rslt['date']  # date of charge, find matching job number from this

            yest, today, tommo = get_dates(expdate)  # parse all 3; day before, day of and after then which one matches the job? format as mm/dd/yyyy
            print(f" dates from format conv: {yest}, {today}   {tommo}")
            if fmt_date(today) in wk_dates.keys():
                print(f" job was same day: get this work order {today}")
                wonum = wk_dates[fmt_date(today)]
            elif fmt_date(yest) in wk_dates.keys():
                print(f" job was yesterday: get previous work order: {yest}")
                wonum = wk_dates[fmt_date(yest)]
            elif fmt_date(tommo) in wk_dates.keys():
                print(f" the job is tomorrow: get next day number: {tommo}")
                wonum = wk_dates[fmt_date(tommo)]

            vendor = rslt['vendor']['name']
            paid_thr = rslt['payment']['card_number']  # raw data for which CC it is on, if found
            notes = ""
            account = rslt['category']  # for which expense category/ expense account in books
            amount = rslt['total']
            details = f"{account} {notes}"    # add more here from specific details like lyft ride info or whatever
            desc_string = f"{details}: {vendor}"

            # parse to here, and pickle the data to finish the code:  
            parsedline = {
                'Expense Date': expdate[:10], 
                'Expense Description': f"{desc_string}\n{make_day_mo(today)}, WO#{wonum}",   # stack up some other data and fill in this one; 
                'Expense Account':account, 
                'Paid Through':paid_thr, 
                'Vendor':vendor, 
                'Expense Amount':amount, 
                'Reference#': wonum, 
                'Is Billable':True, 
                'Customer Name':std_customer, 
                'Is Reimbursable':True,
                }
            # now which ever it is PDF or CSV, rename the pdf for it:
            namedate = today.isoformat()[:10]
            vendor_trunc = vendor[:14]  # shorten the vendor name to something reasonable.. ?
            if ".pdf" in file:
                newname = f"{wonum}_{vendor_trunc.strip()}_{namedate}.pdf"
            elif ".png" in file:
                newname = f"{wonum}_{vendor_trunc.strip()}_{namedate}.png"
            print(f" the renamed filename: {newname}")
            os.rename(exp_dir+file, exp_dir+newname)


    print(f"there were {idx} files in the folder. {parsecount} of them through api.")

    # crunch it all into a dataframe, then spit out the csv file?
    # when it ran?
    now = datetime.today()
    nowfilename = now.isoformat()[:10]
    exp_df = pd.DataFrame.from_dict(parseddata)
    exp_df.to_csv(f"{nowfilename}_ADDexpenses.csv", index=False)






    # with open(ext_file, 'wb') as saveme:
    #     pickle.dump(parseddata, saveme)  # wrote it out for this run...

    # print(f" what are the items from the load?")
    # expfile = f"expenses_{today.isoformat()[:10]}.csv"
    # with open(expfile, 'w') as outfile:
    #     outfile.write(f"Expense Date, Expense Description, Expense Account, Paid Through, Vendor, Expense Amount, Reference#, Is Billable, Customer Name, Is Reimbursable,\n")
    #     for line in parseddata:
    #         outfile.write(f"{line}\n")


    ## now need this to output a useful .csv file which I can import directly to zoho
    """ final rows to have: 
    'Expense Date', 'Expense Description', 
    'Expense Account', 'Paid Through', 'Vendor', 'Expense Amount', 
    'Reference#', 'Is Billable', 'Customer Name', 'Is Reimbursable',
    """