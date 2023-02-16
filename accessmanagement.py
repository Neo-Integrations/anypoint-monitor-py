import subprocess
import comlib
import json
import requests
import logging

def listBusinessGroups(config):
    logger = config['logger']
    appJson = []
    logger.debug("Starting listBusinessGroups");
    cmd  = comlib.anypointCliCmdPrefix(config)
    cmd.append("account")
    cmd.append("business-group")
    cmd.append("list")
    cmd.append("--output")
    cmd.append("json")

    status = subprocess.run(cmd, capture_output=True, text=True)
    logger.debug(f"status=> ${status}")
    if status.returncode == 0:
        try:
            appJson = json.loads(status.stdout)
        except ValueError:
            logger.info("Decoding JSON has failed")
    
    logger.debug("Ending listBusinessGroups")
    return appJson

def listEnvironments(config):
    logger = config['logger']
    appJson = []
    config['env'] = None
    cmd  = comlib.anypointCliCmdPrefix(config)
    cmd.append("account")
    cmd.append("environment")
    cmd.append("list")
    cmd.append("--output")
    cmd.append("json")

    status = subprocess.run(cmd, capture_output=True, text=True)
    if status.returncode == 0:
        try:
            appJson = json.loads(status.stdout)
        except ValueError:
            logger.info(f"Decoding JSON has failed")

    
    return appJson

def getToken(config): 
    logger = config['logger']
    headers = {}
    if config['authStrategy'] == "userPassword":
        url = 'https://anypoint.mulesoft.com/accounts/login'
        headers["content-type"] = "application/json"
        dictPayload = {
            "username": config["username"],
            "password": config["password"]
        }
        data = requests.post(url, data=json.dumps(dictPayload), headers=headers)
        print(data)
    elif config['authStrategy'] == "connectedApp":
        logger.info("")
        url = 'https://anypoint.mulesoft.com/accounts/api/v2/oauth2/token'
        headers["content-type"] = "application/x-www-form-urlencoded"
        dictPayload = {
            "grant_type": "client_credentials", 
            "client_id": config['clientId'],
            "client_secret": config['clientSecret']
        }
        data = requests.post(url, data=dictPayload, headers=headers)
    elif config['authStrategy'] == "refreshToken":
        url = 'https://anypoint.mulesoft.com/accounts/api/v2/oauth2/token'
        headers["content-type"] = "application/x-www-form-urlencoded"
        dictPayload = {
            "grant_type": "refresh_token",
	        "refresh_token": config["refreshToken"],
            "client_id": config['clientId'],
            "client_secret": config['clientSecret']
        }
        data = requests.post(url, data=dictPayload, headers=headers)

    return data.json()