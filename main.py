import apimanager
import accessmanagement
import chmanageapp
import comlib
import csvhandler
import numpy as np
import loggingconfig
import re
from datetime import datetime

logger = loggingconfig.getLogger("APP-USAGE_MINTOR", True)

WORKER_TYPE = {
    "MICRO": 0.1,
    "SMALL": 0.2,
    "MEDIUM": 1,
    "LARGE": 2,
    "XLARGE": 4,
    "XXLARGE": 8,
    "4XLARGE": 16
}

# export ANYPOINT_CLIENT_ID="fb2bf4ede6294c248cb54f429143e30c"
# export ANYPOINT_CLIENT_SECRET="18ef9764D4CC428590FfE657c50Bfa79"
# export ANYPOINT_REFRESH_TOKEN="43846673-8339-49e5-bb11-a8ad1e31e472"

def validateAndCollectAPILevelMetrics(config, apis, report):
    for api in apis:
        apiName = api.get('Asset ID')
        logger.debug(f"API Name is {apiName}")
        config['apiInstanceId'] = api.get('Instance ID')
        apiInstanceId = api.get('Instance ID')

        # Query Policies
        policies = apimanager.listPolicies(config)
        for policy in policies:
            logger.debug(f"Policy Id: {policy.get('Asset ID')}")

            policyId = policy.get('ID')
            policyTemplateId = policy.get('Template ID')
            policyName = policy.get('Asset ID')
            policyStatus = policy.get('Status')
            policyversion = policy.get('Asset Version')
            skipClientIdValidation = False
            jwtKeyOrigin = False
            mandatoryExpClaim = False
            wksUrl = False

            # jwt-policy-validation
            configuration = policy.get('Configuration')
            if policy.get('Asset ID') == 'jwt-validation':
                if len(configuration) > 0:
                    if 'skipClientIdValidation: false' in configuration:
                        skipClientIdValidation = True
                    if 'jwtKeyOrigin: jwks' in configuration:
                        jwtKeyOrigin = True
                    if 'mandatoryExpClaim: true' in configuration:
                        mandatoryExpClaim = True
                    m = re.search("wksUrl:[ ]?([^ ]+)", configuration)
                    if m != None and len(m.groups()) >= 1:
                        wksUrl = m.group(1)
                        logger.info(f"wksURl => {wksUrl}");


            if policy.get('Asset ID') == None:
                config['templateId'] = policyTemplateId
                policyDetails = apimanager.policyDetails(config)
                policyName = policyDetails.get('Name')
                policyCategory = policyDetails.get('Category')
                logger.debug(f"Policy Details: {policyName}")

            report.append([ config['org'], config['env'], apiName, apiInstanceId, policyName, "NA", "NA", "NA","NA", policyStatus])

        # Query Tiers
        tiers = apimanager.listTiers(config)
        for tier in tiers:
            logger.debug(f"Tier Id: {tier.get('Name')}")
            tierId = tier.get('ID')
            slaTierName = tier.get('Name')
            slaTierStatus = tier.get('Status')
            manual = tier.get('Approval')
            report.append([ config.get('org'), config.get('env'), apiName, apiInstanceId, "NA", slaTierName, manual, "NA","NA", slaTierStatus])

        # Query Contracts
        contracts = apimanager.listContracts(config)
        for contract in contracts:
            logger.debug(f"Contracts for the application: {contract.get('Application')}")
            contractApplication = contract.get('Application')
            contractStatus = contract.get('Status')
            clientId = contract.get('Client ID')
            report.append([ config.get('org'), config.get('env'), apiName, apiInstanceId, "NA", "NA", "NA", contractApplication,clientId, contractStatus])


def iterateOverEnvironment(config, environments, report, apiUsageReport, appUsage):
    for env in environments:
        envName = env.get('Name')
        logger.info(f"Organisation=> {config['org']} Environment => {envName}")
        config['env'] = envName
        config['envId'] = env.get('Id')

        apps = chmanageapp.lisAppsV2(config)
        for app in apps:
            appName = app['domain']
            fullDomain = app['fullDomain']
            domain = app['domain']
            numberOfWorker = app['workers']
            key = app['workerType'].upper()
            totalVCores = WORKER_TYPE[key] * numberOfWorker
            usage = chmanageapp.getMuleMessageCount(config, fullDomain)
            timestamp = app['lastUpdateTime'] / 1000
            dateObj = datetime.fromtimestamp(timestamp)
            appUsage.append([ config['org'], config['env'], domain, app['status'], totalVCores, dateObj, usage])

def iterateOverOrganisation(config, bgs, appUsage):
    for bg in bgs:
        orgName = bg.get('Name')
        logger.info(f"Business Group: {orgName}")
        config['org'] = bg.get('Name')
        config['orgId'] = bg.get('Id')
        environments = accessmanagement.listEnvironments(config)
        iterateOverEnvironment(config, environments, appUsage)


def main():
    appUsage = []
    logger.info("Starting ...")

    config = comlib.authConfig()
    config['logger'] = logger
    bgs = accessmanagement.listBusinessGroups(config)

    iterateOverOrganisation(config, bgs, appUsage)
    csvhandler.writeAppUsageReport(config, appUsage)

    logger.info("Ending ...")


try:
    exit(main())
except Exception:
    logger.exception("Exception in main(): ")
    exit(1)