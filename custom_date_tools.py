from datetime import datetime, timedelta
import parsedatetime

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
