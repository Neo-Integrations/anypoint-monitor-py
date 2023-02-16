import subprocess
import comlib
import json
import logging
import requests
from datetime import datetime, timedelta
import time

def listAPIs(config):
    logger = config['logger']
    appJson = []

    cmd  = comlib.anypointCliCmdPrefix(config)
    cmd.append("api-mgr")
    cmd.append("api")
    cmd.append("list")
    cmd.append("--output")
    cmd.append("json")

    status = subprocess.run(cmd, capture_output=True, text=True)
    if status.returncode == 0:
        try:
            appJson = json.loads(status.stdout)
        except ValueError:
            logger.error(status.stdout);
            logger.error(f"Decoding JSON has failed")
    
    return appJson

def listPolicies(config):
    logger = config['logger']
    appJson = []
    
    cmd  = comlib.anypointCliCmdPrefix(config)
    cmd.append("api-mgr")
    cmd.append("policy")
    cmd.append("list")
    cmd.append("--output")
    cmd.append("json")
    cmd.append(f"{config['apiInstanceId']}")

    try:
        status = subprocess.run(cmd, capture_output=True, text=True)
        if status.returncode == 0:
            try:
                appJson = json.loads(status.stdout)
            except ValueError:
                logger.debug(f"Decoding JSON has failed...")
    except Exception as e:
        logger.error(f"Error {e}")
    
    return appJson

def policyDetails(config):
    logger = config['logger']
    appJson = {}
    
    cmd  = comlib.anypointCliCmdPrefix(config)
    cmd.append("api-mgr")
    cmd.append("policy")
    cmd.append("describe")
    cmd.append("--output")
    cmd.append("json")
    cmd.append(f"{config['templateId']}")

    try:
        status = subprocess.run(cmd, capture_output=True, text=True)
        if status.returncode == 0:
            try:
                appJson = json.loads(status.stdout)
            except ValueError:
                logger.debug(f"Decoding JSON has failed")
    except Exception as e:
        logger.error(f"Error {e}")
    
    return appJson

def listTiers(config):
    logger = config['logger']
    appJson = []
    
    cmd  = comlib.anypointCliCmdPrefix(config)
    cmd.append("api-mgr")
    cmd.append("tier")
    cmd.append("list")
    cmd.append("--output")
    cmd.append("json")
    cmd.append(f"{config['apiInstanceId']}")

    try:
        status = subprocess.run(cmd, capture_output=True, text=True)
        if status.returncode == 0:
            try:
                appJson = json.loads(status.stdout)
            except ValueError:
                logger.debug(f"Decoding JSON has failed")
    except Exception as e:
        logger.error(f"Error {e}")
    
    return appJson

def listContracts(config):
    logger = config['logger']
    appJson = []
    
    cmd  = comlib.anypointCliCmdPrefix(config)
    cmd.append("api-mgr")
    cmd.append("contract")
    cmd.append("list")
    cmd.append("--output")
    cmd.append("json")
    cmd.append(f"{config['apiInstanceId']}")

    try:
        status = subprocess.run(cmd, capture_output=True, text=True)
        if status.returncode == 0:
            try:
                appJson = json.loads(status.stdout)
            except ValueError:
                logger.debug(f"Decoding JSON has failed")
    except Exception as e:
        logger.error(f"Error {e}")
    
    return appJson

def apiUsagePerClient(config, apiInstanceId = None, dataArray=[]):
    logger = config['logger']
    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = "Bearer " + config.get('access_token').get('access_token')


    yamlCfg = config.get('yamlCfg')
    duration = yamlCfg['report']['apiUsage']['duration']
    if duration == None:
        duration = 7 # Default duration is last 7 days

    timeNowMinusDelta = datetime.utcnow() - timedelta(days=duration)
    timeNow = timeNowMinusDelta.isoformat()[:-3]+'Z'

    durationInMinute = str(duration * 60 * 24)

    url = "https://anypoint.mulesoft.com/analytics/1.0/" + config['orgId'] + '/environments/'+ config['envId'] + '/query'

    filterForAllAPPIs = {
        "type": "enriched-http-event",
        "aggregators": [
            {
                "dimension": "client_id",
                "limit": 100,
                "order": "descending"
            }
        ],
        "duration": str(durationInMinute) + "m",
        "start_time": timeNow,
        "include_policy_violation": False
    }

    filterForASingleAPIInstance = {
        "type": "enriched-http-event",
        "aggregators": [
            {
                "dimension": "client_id",
                "order": "descending"
            }
        ],
        "duration": str(durationInMinute) + "m",
        "filters": [
            {
                "or": [
                    {
                        "equals": {
                            "api_version_id": str(apiInstanceId)
                        }
                    }
                ]
            }
        ],
        "start_time": timeNow,
        "include_policy_violation": False
    }   


    limit = 100
    delayInSeconds = 5
    for idx in [*range(1, limit, 1)]:
        try:
            data = {}
            if apiInstanceId != None:
                data = requests.post(url, json=filterForASingleAPIInstance, headers=headers)
            else:
                data = requests.post(url, json=filterForAllAPPIs, headers=headers)

            jsonData = data.json()
            break;
        except Exception as e:
            logger.error(f'apimanager->apiUsagePerClient: Call to API Analtics failed.')
            if idx < limit:
                logger.error(f'{idx}: apimanager->apiUsagePerClient: It will be retried...')
                time.sleep(delayInSeconds)
            else:
                logger.error(f'{idx}: apimanager->apiUsagePerClient: No more retry.')

    returnPayload = {}
    index = 0
    for item in jsonData['response']:
        if len(item['client_id']) > 0:
            for client in item['client_id']:
                if client != None:
                    keys = list(client.keys())
                    returnPayload[keys[0]] = (client[keys[0]]).get('count')
                    dataArray.append(keys[0] + ' : ' + str(returnPayload[keys[0]]))
                    index += 1

    return returnPayload

def queryApplications(config):
    url = 'https://anypoint.mulesoft.com/apiplatform/'\
        'repository/v2/organizations/' + config['orgId'] +\
        '/applications?ascending=true&filter=all&limit=250&'\
        'literalMatch=true&offset=0&sort=name&targetAdminSite=true'
    
    apps = {}
    headers = {}
    headers["Authorization"] = "Bearer " + config.get('access_token').get('access_token')
    data = requests.get(url, headers=headers)
    jsonData = data.json()

    for app in jsonData['applications']:
        apps[app['clientId']] = app['name']
    
    return apps