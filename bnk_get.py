import os
from dotenv import load_dotenv
import argparse as ap
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bsp
import time

headless=False

load_dotenv()
PTH = os.getcwd()
starturl = "https://www.chase.com/"




def pull_statement():
    pass

# def 

if __name__ == "__main__":
    user = os.environ.get('BNK')
    authpwd = os.environ.get('BNKAUTH')
    
    options = Options.headless = headless
    driver = webdriver.Firefox(options=options)
    # driver = webdriver.Chrome("chromedriver")

    driver.get(starturl)

    # navigate to log-in and auth page
    time.sleep(3)
    # get iframe and switch
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'logonbox')))
    driver.switch_to.frame(iframe)

    ubox = driver.find_element(By.ID, 'userId-text').click()
    ubox = driver.find_element(By.ID, 'userId-text-input-field').send_keys(user)
    pbox = driver.find_element(By.ID, 'password-text').click()
    ubox = driver.find_element(By.ID, 'password-text-input-field').send_keys(authpwd)
    time.sleep(2)
    submit = driver.find_element(By.ID, 'signin-button').click()
    
    time.sleep(3)


    # navigate to downloads/ statements
    
    # navigate to actual date ranages and get max, or per year
    
    # click to download each one by URL pattern/ iterate all