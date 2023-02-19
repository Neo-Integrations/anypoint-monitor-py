import apimanager
import accessmanagement
import chmanageapp
import comlib
import csvhandler
import numpy as np
import loggingconfig
import re
from datetime import datetime
from threading import Thread
from datetime import datetime, timedelta
import urllib.parse

logger = loggingconfig.getLogger("On-PREM-APP-USAGE", True)

def iterateOverEnvironment(config, environments, appUsage):

    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
    toDate = urllib.parse.quote(now)

    fifteenDaysBack = datetime.now() - timedelta(days=14)
    fifteenDaysBackDate = fifteenDaysBack.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
    fromDate = urllib.parse.quote(fifteenDaysBackDate)

    for env in environments:
        envName = env.get('Name')
        logger.info(f"Organisation=> {config['org']} Environment => {envName}")
        config['env'] = envName
        config['envId'] = env.get('Id')
        apps = chmanageapp.listAppsFromOnPrem(config)
        for app in apps.get('data'):
            appId = app["id"]
            targetServerName = app["target"]["name"]
            appName = app["artifact"]["name"]

            usage = chmanageapp.getOnPremAppUsage(config, appId, fromDate, toDate)

            temp = int(app["artifact"]["lastUpdateTime"]) / 1000
            lastUpdateTime = datetime.fromtimestamp(temp)

            appUsage.append([config['org'], config['env'], targetServerName, appName, app['lastReportedStatus'], lastUpdateTime, usage])
            

def iterateOverOrganisation(config, bgs, appUsage):
    threads = []
    chmanageapp.getInfluxDBUri(config)
    for bg in bgs:
        if bg.get('Name').upper() == "BELRON":
            newConfig = config.copy()
            thread = Thread(target=task, args=(newConfig, bg, appUsage))
            threads.append(thread)
            thread.start()
            break
    for thread in threads:
        thread.join()

def task(config, bg, appUsage):
    orgName = bg.get('Name')
    logger.info(f"Business Group: {orgName}")
    config['org'] = bg.get('Name')
    config['orgId'] = bg.get('Id')
    environments = accessmanagement.listEnvironments(config)
    iterateOverEnvironment(config, environments, appUsage)


def main():
    logger.info("Starting ...")

    appUsage = []
    config = comlib.authConfig()
    config['logger'] = logger
    bgs = accessmanagement.listBusinessGroups(config)

    iterateOverOrganisation(config, bgs, appUsage)
    csvhandler.writeOnPremAppUsageReport(config, appUsage)
    logger.info("Ending ...")

    return 0

try:
    exit(main())
except Exception:
    logger.exception("Something went wrong while running the application")
    exit(1)