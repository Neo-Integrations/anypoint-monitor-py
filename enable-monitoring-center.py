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

def iterateOverEnvironment(config, environments, report):
    for env in environments:
        isSandbox = env.get('Sandbox')
        # Skip production environments
        if isSandbox.upper() == 'N':
            continue

        envName = env.get('Name')
        config['env'] = envName
        config['envId'] = env.get('Id')

        apps = chmanageapp.listAppsFromCloudHub(config)
        for app in apps:
            appName = app.get('domain')
            if app.get('properties'):
                properties = app['properties']
                if properties.get('anypoint.platform.config.analytics.agent.enabled') == None or properties.get('anypoint.platform.config.analytics.agent.enabled') == "false":
                    chmanageapp.updateApplicationProperties(config, appName, properties)
                    report.append([ config['org'], config['env'], appName, app['status']])

                    
            

def iterateOverOrganisation(config, bgs, report):
    threads = []
    for bg in bgs:
        newConfig = config.copy()
        thread = Thread(target=task, args=(newConfig, bg, report))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def task(config, bg, report):
    orgName = bg.get('Name')
    logger.info(f"Business Group: {orgName}")
    config['org'] = bg.get('Name')
    config['orgId'] = bg.get('Id')
    environments = accessmanagement.listEnvironments(config)
    iterateOverEnvironment(config, environments, report)


def main():
    logger.info("Starting ...")

    report = []

    config = comlib.authConfig()
    config['logger'] = logger
    bgs = accessmanagement.listBusinessGroups(config)

    iterateOverOrganisation(config, bgs, report)
    csvhandler.writeEnableMonitoringReport(config, report)

    logger.info("Ending ...")

    return 0

try:
    exit(main())
except Exception:
    logger.exception("Something went wrong while running the application")
    exit(1)