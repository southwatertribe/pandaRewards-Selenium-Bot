# pandaRewards-Selenium-Bot
This is the Python bot that is hosted in AWS Lambda (Corresponds to PandaRewards app)

In order to actually have Selenium and Chromedriver, a layer was created and added to the function. 

Then an endpoint to this function was created which is what the custom API sends a request to with the user's information

Dynamo Db Schema
<img width="646" alt="image" src="https://github.com/southwatertribe/pandaRewards-Selenium-Bot/assets/94877162/e02aabfd-bc13-4425-be93-04c375fa2761">

