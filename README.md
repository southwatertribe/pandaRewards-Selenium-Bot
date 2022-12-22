# pandaRewards-Selenium-Bot
This is the Python bot that is hosted in AWS Lambda (Corresponds to PandaRewards app)

In order to actually have Selenium and Chromedriver, a layer was created and added to the function. 

Then an endpoint to this function was created which is what the custom API sends a request to with the user's information
