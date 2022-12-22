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
    
    message = "Sucess"
    
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
    
    
    for i in range(1,7):
        submitBox = driver.find_element(By.NAME, "CN"+str(i))
        submitBox.send_keys(codeList[i-1])
        
    
    link = driver.find_element(By.ID, "NextButton")
    link.click()
    
    try:
         validate = driver.find_element_by_xpath('//*[@id="errorCN5"]').text
         #validate if it worked then break out if not  
         if validate == "* Error: Please answer this question.":
            message = "Wrong Code!"
         return json.dumps(message)
    except NoSuchElementException:
         message = "Sucess"
    
    #Codes validated do the survey
    
    #Check if there is still buttons to continue 
    link = driver.find_element(By.ID, "NextButton")
    
    #If there is buttons to continue... 
    while len(link) != 0:
        #Check all options
        #radio
        radioButton = driver.find_elements(By.CLASS_NAME, "radioSimpleInput")
        #Text Response Box
        textResBox = driver.find_elements(By.NAME, "S000077")
        #Email
        emailEntry = driver.find_element(By.NAME, "S000057")
        
        #Sleep
        time.sleep(2)
        
        if len(emailEntry) != 0:
            emailConf = driver.find_element(By.NAME, "S000064")
            emailEntry.send_keys(email)
            emailConf.send_keys(email)
        elif len(textResBox) !=0:
            textResBox.send_keys(textres)
        else:
            for i in range(0, len(radioButton), 5):
                radioButton[i].click()
        link[0].click()
            
        
    return json.dumps(message)
