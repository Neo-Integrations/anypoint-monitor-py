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

logger = loggingconfig.getLogger("CLOUDHUB-V1-APP-USAGE", True)

def iterateOverEnvironment(config, environments, appUsage):
    for env in environments:
        envName = env.get('Name')
        logger.info(f"Organisation=> {config['org']} Environment => {envName}")
        config['env'] = envName
        config['envId'] = env.get('Id')

        apps = chmanageapp.lisAppsV2(config)
        for app in apps:
            appName = app.get('domain')
            fullDomain = app.get('fullDomain')
            domain = app.get('domain')
            numberOfWorker = app.get('workers')
            key = app['workerType'].upper()
            totalVCores = comlib.CLOUDHUB_V1_WORKER_TYPE[key] * numberOfWorker
            usage = chmanageapp.getMuleMessageCount(config, fullDomain)
            usages = usage.split(":")
            lastUsedTimeStamp = None
            if usages[1]:
                temp = int(usages[1]) / 1000
                lastUsedTimeStamp = datetime.fromtimestamp(temp)

            lastUpdated = None;
            if app['lastUpdateTime']:
                temp = app['lastUpdateTime'] / 1000
                lastUpdated = datetime.fromtimestamp(temp)

            appUsage.append([ config['org'], config['env'], domain, app['status'], totalVCores, lastUpdated, lastUsedTimeStamp ,usages[0]])
            

def iterateOverOrganisation(config, bgs, appUsage):
    threads = []
    chmanageapp.getInfluxDBUri(config)
    for bg in bgs:
        newConfig = config.copy()
        thread = Thread(target=task, args=(newConfig, bg, appUsage))
        threads.append(thread)
        thread.start()
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
    csvhandler.writeAppUsageReport(config, appUsage)
    logger.info("Ending ...")

    return 0

try:
    exit(main())
except Exception:
    logger.exception("Something went wrong while running the application")
    exit(1)