import subprocess
import comlib
import json
import requests
import accessmanagement
import http
import http.client as http_client

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

def lisAppsV2(config):
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

def getMuleMessageCount(config, fullDomain):
    logger = config['logger']
    headers = {}

    getInfluxDBUri(config)


    params = 'db=%22' + config['influxdbDatabase'][1:-1] + '%22&q=SELECT%20sum(%22messageCount%22)%20FROM%20%22app_stats%22%20WHERE%20(%22org_id%22%20%3D%20\'' + config['orgId'] + '\'%20AND%20%22env_id%22%20%3D%20\'' + config['envId'] + '\'%20AND%20%22app_id%22%20%3D%20\'' + fullDomain + '\')%20AND%20time%20%3E%3D%20now()%20-%2030d%20GROUP%20BY%20time(30d)%2C%20%22app_id%22%20fill(0)%20tz(\'Europe%2FLondon\')&epoch=ms'

    url = 'https://anypoint.mulesoft.com/monitoring/api/visualizer/api/datasources/proxy/'+ str(config['influxdbId']) +'/query?' + params
    headers["Authorization"] = "Bearer " + config['access_token']['access_token']

    usage = 0
    try:
        response = requests.get(url, headers=headers)
        payload = response.json()

        if payload['results']:
            for eachResult in payload['results']:
                if eachResult.get('series'):
                    for eachSeries in eachResult['series']:
                        if eachSeries.get('values'):
                            for eachValue in eachSeries['values']:
                                usage = usage + eachValue[1]
    except Exception:
        logger.exception("Exception while getting the applications")

    return usage

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
            config['influxdbDatabase'] = payload['Settings']['datasources']['influxdb']['database']
            
        except Exception:
            logger.exception("Exception while querying influxdb settings")