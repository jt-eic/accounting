# this version as a derivitave from original save_tollreceipts file.
# build as a class or group of classes to carry out steps. Pass in user data,
# return expense items and image of the receipt.
import re
import pandas as pd
##import inv_functions as inv
import os, shutil
from os import path
from datetime import datetime, date, timedelta
import dateparser
try:
    from .connect_db import user_expemail_creds, get_job_exp_detail, add_expense, date_to_db
except ImportError:
    from connect_db import user_expemail_creds, get_job_exp_detail, add_expense, date_to_db


'''
Built from original version which used pandas primarily to handle the job data and details.
Now runs from sqlite database and django models.
'''


def day_plus_one(d):

    try:
        dt = dateparser.parse(d)
        plus = dt + timedelta(days=1)
        f = datetime.strftime(plus, '%Y-%m-%d')
    except TypeError:
        plus = d + timedelta(days=1)
        f = datetime.strftime(plus, '%Y-%m-%d')

    return f


def day_minus_one(d):

    try:
        dt = dateparser.parse(d)
        plus = dt + timedelta(days=-1)
        f = datetime.strftime(plus, '%Y-%m-%d')
    except TypeError:
        plus = d + timedelta(days=-1)
        f = datetime.strftime(plus, '%Y-%m-%d')

    return f


def ride_direction(file, home, work): 
    '''
    attempt to make a step that reads the file and by determining origin or destination, can tell
    which date/job this expense belongs to.
    If origin is airport, check back a day for arriving home from job.
    if destination is airport, check ahead a day for leaving to a job.
    '''
    ridefile = pd.read_csv(file)
        
    rides = ridefile.to_dict('records')

    print('made to df then dict: ', rides)
    
    hm = home
    wk = work  #  make this an argument from outside, now from user params.
    
    dlist = []
    print('list of stuff', rides)
    
    # best way here is to loop through twice, only looking in single column to determine if
    # leaving for work or returning. ONLY for expenses which jobs are not the same day.
    for i in rides:
        if work in i['origin']: # eval work(airport) starts ride, therefor going home. job yesterday.
            odate = i['date']
            jdate = day_minus_one(odate)
            dlist.append(jdate)
        
    for i in rides:
        if work in i['destination']: # eval work(airport) ends ride, therefor leaving. Job tomorrow.
            odate = i['date']
            jdate = day_plus_one(odate)
            dlist.append(jdate)

    # should one or the other fail, it should still bring in at least one value for this list.
    job_date = max(dlist)

    # only pass back the max value.  
    return job_date


def venue_ride(file):
    pass
    ''' try to make a function that defaults to finding expense data for rides on the day of the job'''

def rmpt(item):
    ''' simple funciton to remove some punctuation from any string'''
    cleaned = re.sub(r'[^\w\s]', '', item)
    return cleaned


def job_vars(jobdict):
    '''
    one function to break out user job into single vars;
    owner_id,
    date,
    customer,
    duration * not sure why duration is there for now, but whatever.
    '''
    for item in jobdict:
        uid = item
        lst = jobdict[uid]
        dateval = lst[0]
        jobnum = lst[1]
        cust = lst[2]
        dur = lst[3]
        
        print(uid)
        print('all the stuff sent in:\n', lst)
        return uid, dateval, jobnum, cust, dur
    

def lyft_file():
    '''
    trying to separate out the file operations from the work being done. parse throught the dir
    and get a csv, should only be ONE to come about per run from this.
    '''
    basepath = path.dirname(__file__)  # begin from the existing file path

    movedir = path.abspath(path.join(basepath, "..", "..", "..", "receipts/ran_expenses"))
    workdir = path.abspath(path.join(basepath, "..", "..", "..", "receipts/"))
    csv_list = []

    # get all csv files
    for file in os.listdir(workdir):
        print('files in directiry', file)
        if file.endswith('.csv'):
            print('found a csv ->', os.path.join(workdir, file))
            csv_list.append(file)
        else:
            print('no csv')
            csv_list.append('na.csv')

    for i in csv_list:
        print('checking CSVs for ride_report:')
        if 'ride_report' in i:
            print('got report, should only be ONE: ', i)
            file_combined = os.path.join(workdir, i)
            dest = os.path.join(movedir, i)
            print('\nthe directory and file: ', file_combined)
            break
    try:
        return csv_list, file_combined, dest
    except:
        file_combined = 'N/A'
        dest = 'N/A'
        return csv_list, file_combined, dest

    
def loop_lyft(file, dest, owner, jobno, cust):
    '''
    now a better version; using file, dest, owner, job_num, customer. 
    '''

    working_file = file

    # make the csv file into a pandas dataframe
    ride_basefile = pd.read_csv(working_file) # bring in the data at first

    print('within tools, this is the file before looping it:\n', ride_basefile)

    # build the vars to grab data from the file:
    for item in ride_basefile.index:
        # pulls date and format correctly
        date = ride_basefile.at[item, "date"]
        ride_date = date_to_db(date)
        # pull the amount value
        total_raw = ride_basefile.at[item, "total"]
        total = re.sub("\$", "", total_raw)
        print("total value minus $ sign?", total)
        # pull the ride_purpose value as
        purpose = ride_basefile.at[item, "ride_purpose"]
        print("purpose val extracted: ", purpose)

        exp_category = 1

        # now to stuff this into the expense document:
        # (date, categoryid, amount, description, billable, ref_no, customer)
        add_expense(date=ride_date,
                    categoryid=exp_category,
                    amount=total,
                    description=purpose,
                    billable= "True",
                    ref_no= jobno,
                    customer= cust,
                    owner_id = owner)


    # now move the file when done.
    shutil.move(file, dest)
    print('tool done, and moved the file from:\n',file, '\nto:', dest)


def get_lyft(file, dest, ownerdct):
    '''
    eventually; will pass in args relating to which user; user directory for saving the files,
    var input relates to a dictionary with {owner_id: [date, jobnum, customer, duration]}
    later need to include the custom path where to put that users file after processing.
    '''

    # this comes from old version, where owner dict was built from back date, and make dict from user info.
    owner, jobdate, jobnum, customer, hours = user_vars(ownerdct) 


    working_file = file

    # make the csv file into a pandas dataframe
    ride_basefile = pd.read_csv(working_file) # bring in the data at first

    print(ride_basefile)


    # build the vars to grab data from the file:
    for item in ride_basefile.index:
        # pulls date and format correctly
        date = ride_basefile.at[item, "date"]
        ride_date = date_to_db(date)
        # pull the amount value
        total_raw = ride_basefile.at[item, "total"]
        total = re.sub("\$", "", total_raw)
        print("total value minus $ sign?", total)
        # pull the ride_purpose value as
        purpose = ride_basefile.at[item, "ride_purpose"]
        print("purpose val extracted: ", purpose)

        exp_category = 1

        # now to stuff this into the expense document:
        # (date, categoryid, amount, description, billable, ref_no, customer)
        add_expense(date=ride_date,
                    categoryid=exp_category,
                    amount=total,
                    description=purpose,
                    billable= "True",
                    ref_no= jobnum,
                    customer= customer,
                    owner_id = owner)

    # now move the file when done.
    shutil.move(file_combined, dest)
    print('ran successful for expense.')



def jdate_decide(ride, home, work):
    ''' finds the date based on which way the ride goes, and passes back a date value which should match for a job.
    the 'ride' argument in is a dictionary item from the '''
    air = 'Airport'
    alt_dest = ['to airport', 'to Airport', 'Terminal East', 'Terminal West', '80249',]
    alt_origin = ['from airport', 'from Airport', 'Airport to', 'airport to']
    
    ride_date = date_to_db(ride['date'])  # pull the date and format it now
    print('************\nworking with this expense:\n', ride)
    # first check
    if work in ride['origin']: # eval work(airport) starts ride, therefor going home. job yesterday.
        odate = ride['date']
        jdate = day_minus_one(ride_date)
        
    elif work in ride['destination']: # eval work(airport) ends ride, therefor leaving. Job tomorrow.
        odate = ride['date']
        jdate = day_plus_one(ride_date)
        
    else:
        if air in ride['origin']:
            print('start at airport, job was yesterday')
            jdate = day_minus_one(ride_date)
        elif air in ride['destination']:
            print('going to airport, job is tomorrow')
            jdate = day_plus_one(ride_date)
        else:
            if ride['ride_purpose']:
                for i in alt_dest:
                    if i in ride['ride_purpose']:
                        jdate = day_minus_one(ride_date)
                        break
                    else:
                        for i in alt_origin:
                            if i in ride['ride_purpose']:
                                jdate = day_plus_one(ride_date)
            else:
                print(f"ride purpose field empty, what else?")
                pauser = input('waiting here for what to do')

    return jdate


def find_jdate(ride, evdates):
    ''' trying to sort which date the ride will resolve to a matched job date;, perhaps IF
    no other match is found? maybe nest this into the other function?
    The 'ride' is a ready dict, so rip out some vars first. Make pieces iterable; ready for
    some map operations.
    '''
    rdate_up = ''
    rdate_dn = ''
    # eval if ANYTHING about the date is at home?
    purp = list(map(rmpt, ride['ride_purpose']))
    dest = list(map(rmpt, ride['destination']))
    orig = list(map(rmpt, ride['origin']))
    ridestops = dest + orig
    rdate_up= day_plus_one(ride['date'])
    rdate_dn = day_minus_one(ride['date'])
    jdate = None
    for job in evdates:
        
        if job in rdate_up:
            print('found match for next day', rdate_up)
            jdate = rdate_up
            break  # if found, can stop and 
        
        elif job in rdate_dn:
            print('found match for day before: ', rdate_dn)
            jdate = rdate_dn
            break
        else:
            print('none match, keep looking')        

    return jdate
            

def lyft_insert(ride, oid, home, work, jobs, attach):
    ''' from here, determine which job the ride goes to, and insert the details to the db'''
    # get ride vars from the ride:
    rdate = date_to_db(ride['date'])
    print('ride date', rdate)
    print('could be problem with jobs list?\n', jobs.index.values)

    if rdate in jobs.index.values:
        jdate = rdate  # lands on same day if taking ride on show day, IE travel work, or to/from
    else:
        try:
            jdate = find_jdate(ride, list(jobs.index.values)) #eval what is up with a ride on non-show days
        except TypeError:
            jdate = jdate_decide(ride, home, work)

    if not jdate:
        return None # this simplifies any further eval of this function and kicks back to main flow.

    cost = ride['total']
    total = re.sub('\$', '', cost)
    ridepurp = ride['ride_purpose']

    # get job specs from db:
    print(jdate, '<<< wtf is the format?', type(jdate))
    cust = 'unknown'
    try:
        cust = jobs.at[jdate, 'Customer']
        jobno = jobs.at[jdate, 'Work Order']
    except KeyError:  # from other db, case matters in model
        cust = jobs.at[jdate, 'customer']
        jobno = jobs.at[jdate, 'work_order']
    exp_category = "Travel Expense"  # derive this category from the db expense categories foreign keys

    # combine stuff for description field:
    wkday = dateparser.parse(jdate).strftime("%a %b, %d ")
    purpose = ridepurp +"\n" + wkday + ' WO# ' + str(jobno)
    # it all comes to this: insert to db
    print('just before insert, what date?', rdate)
    exp_dict = {"Expense_Date": rdate, "Expense Category": exp_category,
                "Expense Amount": total, "Expense_Description": purpose,
                "Is Billable": "True", "ReferenceNo": jobno,
                "Customer_Name": cust, "receipt_file": attach,
                "owner_id": oid,}

    return exp_dict


if __name__ == '__main__':
    file = pd.read_csv('testlyft.csv')
    dct = file.to_dict('records')
    home = '13395 Monroe Way, Thornton CO 80241'
    work = 'Airport, Denver'

    for ride in dct:
        print('the ride:\n', ride)
        dt_cap = jdate_decide(ride, home, work)
        print('end of loop, what is the captured?\n', dt_cap, '\n**********************')
