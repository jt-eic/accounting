import os
import parsedatetime
from datetime import datetime, timedelta
import pandas as pd
import csv


'''12-18-2022:
each line; match date.
get job numb, and re-format the line,
'''

def reformat_lyft(ridedata):
    ''' takes the line and re'''
    pass


def which_job_date(purp):
    ''' using the ride purpose line, figure out which direction to move the date for the job it matches
    to. if 'venue' in the purpose, easily is the same day.
    if '''
    if 'venue' in purp:
        return 0
    if 'hotel from airport' in purp:
        return 1
    if 'hotel to airport' in purp:
        return -1


def parse_ride(rideline) -> dict:
    '''take a ride line and pass back which date the job would match up:'''
    datadate = rideline['date'][:10]
    rdate = datetime.strptime(datadate, "%Y-%m-%d")  # immediately use the parser, real date can be operated on
    purpose = rideline['ride_purpose']  #combine with the job number, and day, mo date format.
    # wtf with the purpose:
    jobdate = rdate + timedelta(days=which_job_date(purpose))

    compiled = {
        'total': float(rideline['total'].replace('$', '')),  # remove $ sign and make float
        'purpose': purpose, # make it contain the purpose, 
        'category': 'Travel Expense',
        'ridedate': rdate.isoformat(),
        'jdate': jobdate,
        }

    return compiled


if __name__ == '__main__':
    basedir = "current expenses\\"
    files = os.listdir(basedir)
    for file in files:
        if "csv" in file:
            ridedf = pd.read_csv(basedir+file)
            data = ridedf.to_dict('records')
            print(f"\n*****************\nThIS CSV: {file} and the data:")
            for ride in data:
                jobdate, details,  = parse_ride(ride)

                
                # wtf with the date

