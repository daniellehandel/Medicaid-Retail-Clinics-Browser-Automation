# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 17:28:27 2020

@author: DanielleHandel
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import numpy as np


PATH = r"C:\Program Files (x86)\chromedriver.exe"

#%%
zipmed = pd.read_excel(r"C:/Users/asyah/Desktop/Fall 2020/Medicaid/ffs_clinics.xlsx", dtype = {'zip' : str , 'County.Code' : str}, sheet_name = "Clinic Numbers")

#%%
def cvsScrape(mcaids, locations, nums, addresses, donezips):
    for insure, state in zip(mcaids, locations):
        
        driver = webdriver.Chrome(PATH)
        
        driver.get("https://www.cvs.com/minuteclinic/insurance-and-billing/insurance-check")
        
        time.sleep(1)    
        
        #deal with pop-up that asks first-time users to fill out a survey
        try:
            nothanks = driver.find_element_by_xpath("//a[@title='No, thanks']")
            nothanks.click() 
        except NoSuchElementException:
            pass
        
        while True:
            try:
                #select an insurance carrier
                WebDriverWait(driver, 15).until\
                (EC.presence_of_element_located((By.XPATH , "//select[@id='choose_carrier']"))) # this will click the element if it is there
                
                #if this does not work, refresh the page until it does
            except NoSuchElementException:
                driver.refresh() 
                try:
                    nothanks = driver.find_element_by_xpath("//a[@title='No, thanks']")
                    nothanks.click() 
                except NoSuchElementException:
                    pass
                           
            finally:            
                try:
                    Select(driver.find_element_by_xpath("//select[@id='choose_carrier']")).select_by_visible_text(insure) 
                except NoSuchElementException:
                    driver.refresh()
                    time.sleep(2)
                    try:
                        nothanks = driver.find_element_by_xpath("//a[@title='No, thanks']")
                        nothanks.click() 
                    except NoSuchElementException:
                        pass
                    
                    #select the appropriate FFS Medicaid program from the dropdown
                    Select(driver.find_element_by_xpath("//select[@id='choose_carrier']")).select_by_visible_text(insure)
                
                break       
        #check again for the pop-up     
        try:
            nothanks = driver.find_element_by_xpath("//a[@title='No, thanks']")
            nothanks.click() 
        except NoSuchElementException:
            pass
        
        time.sleep(3)
        
        #use java to click the "next" button regardless of popups that may be blocking
        nextbutton1 = driver.find_element_by_xpath("//button[@id='nextBtnCarrier']")
        driver.execute_script("arguments[0].click();", nextbutton1)
        
        try:
            nothanks = driver.find_element_by_xpath("//a[@title='No, thanks']")
            nothanks.click() 
        except NoSuchElementException:
            pass
        
        #type the zip code one character at a time, for timing purposes
        zipcode = driver.find_element_by_xpath(" //input[@id='find-clinic']")
        for i in range(5):
            time.sleep(.5)
            zipcode.send_keys(state[i])
            time.sleep(.5)
            
        time.sleep(5)
        
        #hit enter
        zipcode.send_keys(Keys.RETURN)
        
        time.sleep(5)
        
        #if there are more than 5 clinics, a "view more" button will appear. click it.
        try:
            more = driver.find_element_by_xpath('//body/app-root/app-side-nav/div/div/app-insurance-check/main/div/div/div/div/div/div/div/div/div/div/div/div/app-clinic-list/div/div/button[1]')
            more.click() 
        except NoSuchElementException:
            pass
        
        time.sleep(10)    
        
        #record the number of clinic boxes returned by the search
        try:
            driver.find_element_by_class_name("clinicDetails")
            nums.append(len(driver.find_elements_by_class_name('clinicDetails')))
        except NoSuchElementException:
            pass
            nums.append(0)
    
        #record the address of each clinic 
        try:
            onezip = []
            addresslist = list(driver.find_elements_by_tag_name('address'))
            for each in addresslist:
                onezip.append(each.text)
            addresses.append(onezip)
        except NoSuchElementException:
            pass
            addresses.append('none')
            
        donezips.append(state)
        
        print()    
        driver.close()

#%%

#set empty arrays
nums = []
addresses = []
donezips = []

#%%

#run using list of FFS state Medicaids and the most populous zip code in each county 
cvsScrape(zipmed["Associated.FFS"].tolist(), 
          zipmed["zip"].tolist(),
          nums, addresses, donezips)


#%%

#make this data into a nice dataframe
addresses_df = pd.DataFrame({'zip' : donezips, 'mcaid' : zipmed['Associated.FFS'], 
                        'nums' : nums, 'addresses' : addresses})
#%%

#print to excel doc

import openpyxl as opx

addresses.to_excel(r'C:/Users/asyah/Desktop/Fall 2020/Medicaid/addresses.xlsx', index=False)

