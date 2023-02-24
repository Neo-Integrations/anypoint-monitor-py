import subprocess
import comlib
import json
import requests



def queryApplicationDetails(config, appName):
    cmd  = comlib.anypointCliCmdPrefix(config)
    cmd.append("runtime-mgr")
    cmd.append("cloudhub-application")
    cmd.append("describe-json")
    cmd.append(f"{appName}")

    status = subprocess.run(cmd, capture_output=True, text=True)
    appJson = None
    if status.returncode == 0:
        appJson = json.loads(status.stdout)
    else:
        print(f"Something went wrong. Error: {status.stderr}")
    
    return appJson

def lisApps(config):
    logger = config['logger']
    cmd  = comlib.anypointCliCmdPrefix(config)
    cmd.append("runtime-mgr")
    cmd.append("cloudhub-application")
    cmd.append("list")
    cmd.append("--output")
    cmd.append("json")

    status = subprocess.run(cmd, capture_output=True, text=True)
    appJson = {}
    if status.returncode == 0:
        try:
            appJson = json.loads(status.stdout)
        except ValueError:
            logger.error(status.stdout)
            logger.error(f"Decoding JSON has failed. Programme will continue...")
    else:
        print(f"Something went wrong. Error: {status.stderr}")
    
    return appJson

def listAppsFromCloudHub(config):
    logger = config['logger']
    headers = {}

    url = 'https://anypoint.mulesoft.com/cloudhub/api/applications'
    headers["Authorization"] = "Bearer " + config['access_token']['access_token']
    headers["X-ANYPNT-ENV-ID"] = config['envId']
    headers["X-ANYPNT-ORG-ID"] = config['orgId']

    payload = {}
    try:
        response = requests.get(url, headers=headers)
        payload = response.json()
    except Exception:
        logger.exception("Exception while getting the applications")

    return payload

def listAppsFromOnPrem(config):
    logger = config['logger']
    headers = {}

    url = 'https://anypoint.mulesoft.com/armui/api/v1/applications'
    headers["Authorization"] = "Bearer " + config['access_token']['access_token']
    headers["X-ANYPNT-ENV-ID"] = config['envId']
    headers["X-ANYPNT-ORG-ID"] = config['orgId']

    payload = {}
    try:
        response = requests.get(url, headers=headers)
        payload = response.json()
    except Exception:
        logger.exception("Exception while getting the applications")

    return payload

def getMuleMessageCount(config, fullDomain):
    logger = config['logger']
    headers = {}
    params = 'db=%22' + config['influxdbDatabas'][1:-1] + '%22&q=SELECT%20sum(%22messageCount%22)%20FROM%20%22app_stats%22%20WHERE%20(%22org_id%22%20%3D%20\'' + config['orgId'] + '\'%20AND%20%22env_id%22%20%3D%20\'' + config['envId'] + '\'%20AND%20%22app_id%22%20%3D%20\'' + fullDomain + '\')%20AND%20time%20%3E%3D%20now()%20-%2090d%20GROUP%20BY%20time(5d)%2C%20%22app_id%22%20fill(0)%20tz(\'Europe%2FLondon\')&epoch=ms'
    url = 'https://anypoint.mulesoft.com/monitoring/api/visualizer/api/datasources/proxy/'+ str(config['influxdbId']) +'/query?' + params
    headers["Authorization"] = "Bearer " + config['access_token']['access_token']

    usage = 0
    values ={}
    try:
        response = requests.get(url, headers=headers)
        payload = response.json()
        if payload['results']:
            for eachResult in payload['results']:
                if eachResult.get('series'):
                    for eachSeries in eachResult['series']:
                        if eachSeries.get('values'):
                            for eachValue in eachSeries['values']:
                                values[eachValue[0]] = eachValue[1]
                                usage = usage + eachValue[1]
    except Exception:
        logger.exception("Exception while getting the applications")
    
    returnPayload = str(usage) + ":"
    if len(values) > 0:
        keys = list(values.keys())
        keys.sort(reverse=True)
        for key in keys:
            if values[key] > 0:
               returnPayload = returnPayload + str(key)
               break

    return returnPayload

def getInfluxDBUri(config):
    if config.get('influxdbId'):
        return
    else:
        logger = config['logger']
        headers = {}

        url = 'https://anypoint.mulesoft.com/monitoring/api/visualizer/api/bootdata'
        headers["Authorization"] = "Bearer " + config['access_token']['access_token']

        uri = {}
        usage = 0
        try:
            response = requests.get(url, headers=headers)
            payload = response.json()
            
            config['influxdbId'] = payload['Settings']['datasources']['influxdb']['id']
            config['influxdbDatabas'] = payload['Settings']['datasources']['influxdb']['database']
            
        except Exception:
            logger.exception("Exception while querying influxdb settings")

def getOnPremAppUsage(config, appId, fromDate, toDate):

    logger = config['logger']
    headers = {}

    url = 'https://anypoint.mulesoft.com/monitoring/query/api/v1/organizations/'+ config['orgId'] +'/environments/' + config['envId'] + '/applications?from='+ fromDate +'&to=' + toDate + '&detailed=true'
    headers["Authorization"] = "Bearer " + config['access_token']['access_token']
    headers["content-type"] = "application/json"

    dictPayload = {
        "ids": [appId]
    }

    usage = 0
    try:
        response = requests.post(url, data=json.dumps(dictPayload), headers=headers)
        payload = response.json()
        
        for app in payload.get('applications'):
            if app.get('metrics') and app['metrics'].get('message-count') and app['metrics']['message-count'].get('aggregate'):
                usage = usage + app['metrics']['message-count']['aggregate']['sum']
                
        
    except Exception:
        logger.exception("Exception while querying influxdb settings")
    
    return usage


def updateApplicationProperties(config, appName, properties):

    logger = config['logger']
    orgId = config['orgId']
    envId = config['envId']

    headers = {}

    url = 'https://anypoint.mulesoft.com/monitoring/api/v2/settings/cloudhub/organizations/' + orgId +  '/environments/' + envId + '/applications/' + appName

    headers["Authorization"] = "Bearer " + config['access_token']['access_token']
    headers["content-type"] = "application/json"

    properties['anypoint.platform.config.analytics.agent.enabled'] = "true"

    dictPayload = {
        "applicationId": "",
        "applicationName": appName,
        "properties": properties
    }

    try:
        response = requests.put(url, data=json.dumps(dictPayload), headers=headers)
        payload = response.json()
        
    except Exception:
        logger.exception("Exception while querying influxdb settings")
        return False
    
    return True