#survey_task lambda
#Survey_task lambda that creates a temporary task in the database
#Triggers panada_bot lambda
try:
    import json
    import time
    import os
    import shutil
    import uuid
    import boto3
    from datetime import datetime
    import datetime

    print("All Modules are ok ...")

except Exception as e:

    print("Error in Imports ")



def store_task_status(task_id, status, table, result=None):
    table.put_item(
        Item={
            'task_id': task_id,
            'status': status,
            'result': result
        }
    )

def invoke_second_lambda(lambda_client, function_name, task_id, original_event):
    payload = {
        "task_id": task_id,
        "original_event": original_event
    }
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )



def lambda_handler(event, context):
    
     # TODO implement
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('survey_tasks')
    task_id = str(uuid.uuid4())
    store_task_status(task_id, 'pending', table)
  
  
    lambda_client = boto3.client('lambda')
    second_lambda_function_name = "PandaBot3_7"
    invoke_second_lambda(lambda_client, second_lambda_function_name,task_id, event)
    
   
    response = {
        'statusCode': 200,
        'body': json.dumps({"task_id": task_id}),
        'headers': {
            'Content-Type': 'application/json',
        }
        
    }
    return response





#panda_bot lambda 
#Bot that gets triggered by the survey lambda function 
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

def update_task_status(task_id, status, result):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('survey_tasks')
    table.update_item(
        Key={'task_id': task_id},
        UpdateExpression='SET #status = :status, #result = :result',
        ExpressionAttributeNames={
            '#status': 'status',
            '#result': 'result',
        },
        ExpressionAttributeValues={
            ':status': status,
            ':result': result,
        }
    )


def lambda_handler(event, context):
    
    #Initialize default message
    message = "success"
    
    #Instantiate driver and go to panda survey
    instance_ = WebDriver()
    driver = instance_.get()
    driver.get("https://www.pandaguestexperience.com/")
    
    
    #CREATE DICTS
    objectDict = json.loads(event['original_event']['body'])
    mainDict = objectDict['entry']
    the_id = event['task_id']
    codeDict = mainDict["code"]
    print(codeDict.keys())
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
            print("WRONG CODE BABYYY")
            message = "Wrong Code!"
            status = "success"
            result = message
            update_task_status(the_id,status,result)
         return json.dumps(message)
    except NoSuchElementException:
         message = "success"
    
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
        
    status = 'success'
    result = message
    #Update tasks
    update_task_status(the_id,status,result)
        
    return json.dumps(message)
