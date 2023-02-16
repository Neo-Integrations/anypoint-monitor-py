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
            timestamp = app['lastUpdateTime'] / 1000
            dateObj = datetime.fromtimestamp(timestamp)
            appUsage.append([ config['org'], config['env'], domain, app['status'], totalVCores, dateObj, usage])
            

def iterateOverOrganisation(config, bgs, appUsage):
    threads = []
    for bg in bgs:
        thread = Thread(target=task, args=(config, bg, appUsage))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def task(config, bg, appUsage):
    newConfig = config.copy()
    orgName = bg.get('Name')
    logger.info(f"Business Group: {orgName}")
    newConfig['org'] = bg.get('Name')
    newConfig['orgId'] = bg.get('Id')
    environments = accessmanagement.listEnvironments(newConfig)
    iterateOverEnvironment(newConfig, environments, appUsage)


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