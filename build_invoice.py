import aiohttp
import pandas as pd
import asyncio, random, json
from datetime import datetime, timedelta  # using this as the date formats from portal are simple: mm/dd/yyyy and use strptime
from dotenv import load_dotenv
import os, sys
import time
import pickle

''' this step: building an invoice is a small part of a larger system. Use of dates, job numbers and other job information
is re-organized into a range of single line-items for purposes of invoicing. The invoice items are derived from another 
source; a .csv file containing 'items' with basic descriptions and prices. IE: EIC (day rate) based job, overtime past 10
hours, travel days, per diem. All of which billable items make up a full invoice.

This will output a .csv file with todays date for a start. Then need to weed out duplicate line items or redundant travel day
lines, to complete the .csv file for importing to zoho books invoices. 

work toward: 
make the compiled data a dataframe, then combine multiple per-diem items. Per diem needs to only be ONE line, with the 
quantity sum of the date range of the invoice.
* travel days may need to be manually cleaned up. sometimes there are only 2: leaving and returning home. 
Sometimes there are more in-between show EIC days. There is no exact science. Eventually; IF there are more than 1 days 
between EIC rows, then it can probably leave some travel in between. Or weed them out if day span == 0. 

'''

def day_and_month(strdate: str):
    '''take in the date string as mm/dd/yyyy and reverse it to date object and 
    pass back the day name and month name'''
    dateobj = datetime.strptime(strdate, '%m/%d/%Y')
    newstring = datetime.strftime(dateobj, "%a. %b %d")
    
    return newstring


def back_day(strdate: str):
    ''' take the string and subtract one date value to get travel day prior.  returns Mon Jan 1 ex.'''
    dateobj = datetime.strptime(strdate, '%m/%d/%Y')
    dayminus = dateobj - timedelta(days=1)
    return datetime.strftime(dayminus, "%a. %b %d")


def forward_day(strdate: str):
    ''' take the string and add one for the next day. returns Mon Jan 1 ex.'''
    dateobj = datetime.strptime(strdate, '%m/%d/%Y')
    dayplus = dateobj + timedelta(days=1)
    return datetime.strftime(dayplus, "%a. %b %d")


## formatted and figured out dates for each invoice run
# days_of_week = {0: "Sun", 1: "Mon", 2:"Tues", 3: "Wed", 4: "Thur", 5: "Fri", 6: "Sat", }
today = datetime.today()

todaystr = datetime.strftime(today, "%Y-%m-%d")  # for the date as 'invoice date' as YYYY-MM-DD'
yeststr = today - timedelta(days=1)
duedatestr = datetime.strftime(today + timedelta(days=9), "%Y-%m-%d")
begin = today - timedelta(days=6)
backdate = begin.isoformat() + "Z"
sdate = yeststr.isoformat() + "Z"
dayplus = today + timedelta(days=60)
edate = None
if edate == None:
    edate = dayplus.isoformat() + "Z"
else:
    edate = edate
print('the dates', sdate, edate)

AGENT_LIST = ["Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0",
              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",]
headers = {'User-Agent': random.choice(AGENT_LIST)}


start_url = "https://portal02.mobiletvgroup.com/account/login"
login_url = "https://portal02.mobiletvgroup.com/api/account/login"
loggedin_url = "https://portal02.mobiletvgroup.com/api/account/UserIsLoggedIn"
user_url = "https://portal02.mobiletvgroup.com/api/account/getUser"
events_url = "https://portal02.mobiletvgroup.com/api/filteredevents"


filters = {"startDate":backdate,
            "endDate":sdate,
            "eventCoordinator":"0",
            "visitor":"0",
            "home":"0",
            "feedType":"0",
            "feedName":"0",
            "client":"0",
            "venue":"0",
            "venueState":"0",
            "eIC":"Thomas, Jasun",   # blank here, for everything in portal for the date range
            "subTruck":"0",
            "schoolEventType":"0",
            "eventType":"0",
            "workOrderStatus":"0",
            "mobileUnit":"0",
            "crewer":"0",
            "unitLevel":"0",
            "eventName":"",
            "page":1,
            "sortDirection":"ASC",
            "sortField":"event-coord",
            "league":"0",
            "returnAllResults":"true"}

jar = aiohttp.CookieJar()


async def get_page(session, url):
    async with session.get(url) as r:
        return await r.json()
        # return thepage['eventDetail']  # just sending back details
        

async def get_all(session, joblist):
    event_api = "https://portal02.mobiletvgroup.com/api/event/"
    
    tasks = []    
    
    for wo in joblist:
        url = event_api + str(wo)
        
        task = asyncio.create_task(get_page(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


async def main(url, header, creds):
    async with aiohttp.ClientSession(headers=headers, cookie_jar=jar) as session:
        async with session.get(url) as r:  # similar to pkg from old one
            async with session.post(login_url, json=creds) as s:
                time.sleep(5)
                token = s.cookies['portal-token'].value # this carries the tkn
                token_creds = {"Email": u_email, "UserToken": token}
                async with session.post(loggedin_url, json=token_creds):  ## past this, now get events
                    async with session.post(events_url, json=filters) as evlist:
                        time.sleep(1)
                        pulled = await evlist.json()
                        
                        mainlist = pulled['events']  # from this make a job number list, but throw this to a var first
                        job_numbers = [ev['workOrderNumber'] for ev in mainlist]
                        
                        #now go through and build tasks for the full list:
                        job_details = await get_all(session, job_numbers)
                        
                        
    return mainlist, job_details

mtvg = "Mobile TV Group"


if __name__ == "__main__":
    myname = 'Thomas, Jasun'
    invoice_start = pd.read_csv('invoice_starter.csv')

    # date from sdate for invoice lines:
    invoiced_date = sdate[:10]

    sys.path = sys.path + ["C:\\Users\\jasun\Desktop\\python_stuff\\accounting\\"]
    load_dotenv()  # including the django settings env from .env file


    fields = []
    staff_flds = []
    venuefields = []

    # the safe way to get the portal creds... better than actual env variables. :)
    u_email = os.getenv("USER")
    u_passwd = os.getenv("PSSWD")
    
    creds = {"Email": u_email, "Password": u_passwd, "RememberMe": "true"}
    
    # list of fields from models to use for filtering event data fields
    # eic_homes = pd.read_csv("EIC_list.csv", index_col='name')
    
    start = datetime.now()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    mainjobs, jobdetails = asyncio.run(main(start_url, headers, creds))

    # from here, build invoicing rather than homes or job data. 
    items = pd.read_csv("saleItems.csv", index_col='index')
    # print(items)
    # # get these invoice line items minimum:
    
    exp_jobdict = {}  # stack up what this finds as a date: wonum dictionary to use with expenses later. Temp solution

    for job in jobdetails:
        '''parse out job data: 
        Date; factor before=after date with travel;; I can delete it if not needed? simpler.
        job number = ReferenceNo
        staff[ find ME in the list and get:][index][inTime][outTime][totalTimeHours]  for overtime data
        eventName
        mobileUnit

        get details for travel day, show day, overtime, and per-diem or per-diem HI
        complete headers for invoice:
        Invoice_Date,Invoice_Number,Customer_Name,Item Name,Item Desc,Item Price,Usage Unit,\
            Quantity,Item Total,PurchaseOrder,ReferenceNo,cf.show date,Due Date,CF.event
        '''
        job_r = job['eventReport']  # block of main data to get the rest from
        jobdate = job_r['eventDate']
        truck = job['eventDetail']['truckType']  # for removing things from the lines, or make NOT eic
        eventname = job_r['eventName']
        wo_num = job_r['workOrderNumber']
        evname_lineitem = eventname.replace(f"{truck} ", "")

        staff = job_r['staff']  # for overtime values

        if jobdate not in exp_jobdict.keys():  # add to this for now, import for expense parse later
            exp_jobdict[jobdate] = wo_num

        for eic in staff:
            if myname in eic['employeeName']:
                calltime = eic['inTime']
                outtime = eic['outTime']
                overtime = float(eic['totalTimeHours']) - 10.0
        
        # above here, all data gathered.  Now stack it for inserting to new df
   
        # format the found data and combine with item.csv to create invoice lines
        spec_items = ['eictvl in', 'eic', 'eicot', 'eictvl out', 'perdiem',]
        for item in spec_items:
            tvl_in_day = back_day(jobdate)
            tvl_out_day = forward_day(jobdate)
            job_dayMo = day_and_month(jobdate)

            inv_line = items.loc[item].to_dict()
            inv_line['Customer_Name'] = mtvg
            inv_line['Invoice_Date'] = todaystr  # for each one
            inv_line['Invoice_Number'] = "INV_00  _MTVG"
            inv_line['PurchaseOrder'] = wo_num
            inv_line['ReferenceNo'] = wo_num
            inv_line['cf.show date'] = jobdate
            inv_line['Due Date'] = duedatestr
            inv_line['CF.event'] = evname_lineitem
            
            if 'eictvl in' == item:
                desc_stack = f"Travel\n{tvl_in_day} W.O.#:{wo_num}"
                print(f" TVL in item: {desc_stack}")
            if 'eictvl out' == item:
                desc_stack = f"Travel\n{tvl_out_day} W.O.#:{wo_num}"
                print(f" tvl out item: {desc_stack}")
            if 'eic' == item:
                desc_stack = f"{evname_lineitem}\n{job_dayMo} W.O.#:{wo_num}"
                print(f" eic in item: {desc_stack}")
            if 'eicot' == item:
                desc_stack = f"{job_dayMo} W.O.#:{wo_num}\nstart:{calltime}  end:{outtime}  {overtime} hours"
                print(f" ot in stack: {desc_stack}")
                inv_line['Quantity'] = overtime
            if 'perdiem' == item:
                desc_stack = f"{tvl_in_day} to {tvl_out_day} per diem for ___ location"
            
            inv_line['Item Desc'] = desc_stack
            invoice_start.loc[len(invoice_start.index)] = inv_line
            # print(inv_line)

    with open('workorders.pkl', 'wb') as expfile:
        pickle.dump(exp_jobdict, expfile)
    
    invoice_start.to_csv(f"newinv_{todaystr}.csv", index=False)
                
    
    
    
    # for OT: get report history data.. find that through the http data pull:
    
    
    

    
    
    # prep for export to new csv: : OR just use zoho API!! direct in..
    

    '''  BELOW HERE: is all stuff I don't need for the invoice stuff.
    # gotta add any staff new folks as StaffMembers first, then do link to the job
    for idx, ev in enumerate(jobdetails):  # within here can it add the event once the staff are there?  use ev instance
        mtom_staff = []   # for dumping to manyToMany field for the event created
        staff = ev['eventDetail']['staff']
        for person in staff:
            # pull from the df, put their extra details in here
            upname = person['name'].upper()
            staffadd = {k:v for k,v in person.items() if k in staff_flds}
            try:
                hm = eic_homes.loc[upname].home
                hm = hm.replace(hm[-2:], states.abbrev_to_us_state[hm[-2:]]).upper()
            except KeyError:
                print('not in dataframe. skip..')
                continue
            staffadd['homeLocation'] = hm
            staffadd['mainTruck'] = eic_homes.loc[upname].truck
            per_obj, created = allstaff.update_or_create(name=staffadd['name'], defaults=staffadd)
            mtom_staff.append(per_obj)  # build the list to put in m2m
        evpayload = ev['eventDetail']
        evpayload.update(mainjobs[idx])
        
        evpayload = {k:v for k,v in evpayload.items() if k in fields}

        # raw element for event venue_address PLUS check venues DB, or go parse it if not available        
        venueadd = evpayload['localCoordinatorValues'][-1]['value2']
        if venueadd:
            addys = {'venue_address': venueadd, }
            
            # addys = get_address(evpayload)
            # print(f"*******\ngots any address data?? {addys}\n\n")
            ## This payload filtered by dict items only needed for DB
            # is it in the db?
            # try:
            fromdb = db_venues.filter(portal_name=venueadd).values()
            
            if not fromdb:  # means it is NOT in the db, so build and add it THEN put in the 
                try:
                    parsedaddy = us_addr(venueadd)
                except IndexError:
                    print(f"coming from here? venueadd in except statement: {venueadd}")
                    parsedaddy = find_city_state(venueadd)

                state = parsedaddy['state']

                fromdb = db_venues.create(**parsedaddy)
                addys['city_state'] = f"{parsedaddy['city']}, {parsedaddy['state']}"
                
            else:
                print(f" there is one in the db? {fromdb}")
                addys['city_state'] = f"{fromdb[0]['city']} {fromdb[0]['state']}"
                # pause = input("caught here with one from db. ")
            evpayload.update(addys)  # needs a dict here {venue_address; val, city_state; val}
        ev_rcpt, evcreated = db_events.update_or_create(workOrderNumber=evpayload['workOrderNumber'], defaults=evpayload) #causes match
        print(f"THIS event {ev_rcpt.workOrderNumber} created? {evcreated}. DONE.")
        ev_rcpt.staff.add(*mtom_staff)
        
    ending = datetime.now()
    durr = ending - start

    print(f"this took: {durr} to find {len(jobdetails)} jobs. cool!")

    # cook down the jobs list for details to add to db:
    '''  
