try:
    import json
    import time
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import NoSuchElementException
    import os
    import shutil
    import uuid
    import boto3
    from datetime import datetime
    import datetime

    print("All Modules are ok ...")

except Exception as e:

    print("Error in Imports ")
    

class WebDriver(object):

    def __init__(self):
        self.options = Options()

        self.options.binary_location = '/opt/headless-chromium'
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--start-fullscreen')
        self.options.add_argument('--single-process')
        self.options.add_argument('--disable-dev-shm-usage')

    def get(self):
        driver = Chrome('/opt/chromedriver', options=self.options)
        return driver



def lambda_handler(event, context):
    
    #Initialize default message
    message = "Sucess"
    
    #Instantiate driver and go to panda survey
    instance_ = WebDriver()
    driver = instance_.get()
    driver.get("https://www.pandaguestexperience.com/")
    print(driver.page_source)
    
    #CREATE DICTS
    object = event['body']
    objectDict = json.loads(object)
    mainDict = objectDict["entry"]
    codeDict = mainDict["code"]
    
    #Create code List
    codeList = []
    for key, val in codeDict.items():
        # TODO: write code...
        codeList.append(val)
    #User names
    firstName = mainDict["user"]["f_name"]
    lastName = mainDict["user"]["l_name"]
    #Email
    email = mainDict["user"]["user_email"]
    #textRes
    textRes = mainDict["user"]["textres"]
   
    
    #Submit code
    for i in range(1,7):
        submitBox = driver.find_element(By.NAME, "CN"+str(i))
        submitBox.send_keys(codeList[i-1])
        
    #Button on code submition page
    link = driver.find_element(By.ID, "NextButton")
    link.click()
    
    #Check if code is valid
    try:
         validate = driver.find_element_by_xpath('//*[@id="errorCN5"]').text
         #validate if it worked then break out if not  
         if validate == "* Error: Please answer this question.":
            message = "Wrong Code!"
         return json.dumps(message)
    except NoSuchElementException:
         message = "Sucess"
    
    #Codes validated do the survey
    #Begin surver button
    link = driver.find_elements(By.ID, "NextButton")
    
    #If there is buttons to continue... 
    while len(link) != 0:
        #Check all options
        #radio
        try:
            radioButton = driver.find_elements(By.CLASS_NAME, "radioSimpleInput")
        except NoSuchElementException:
            radioButton = []
            print("skip")
        #Text Response Box
        try:
            textResBox = driver.find_elements(By.NAME, "S000077")
        except NoSuchElementException:
            textResBox = []
            print("skip")
        #Email
        try:
            emailEntry = driver.find_elements(By.NAME, "S000057")
        except NoSuchElementException:
            emailEntry = []
            print("skip")
        
        #Check what part of the survey we are in
        if len(emailEntry) != 0:
            emailConf = driver.find_elements(By.NAME, "S000064")
            emailEntry[0].send_keys(email)
            emailConf[0].send_keys(email)
        elif len(textResBox) !=0:
            textResBox[0].send_keys(textRes)
        else:
            for i in range(0, len(radioButton), 5):
                radioButton[i].click()
                
        #Check if we need to continue the survey 
        link = driver.find_elements(By.ID, "NextButton")
        if len(link) == 0:
            break
        link[0].click()
            
        
    return json.dumps(message)
