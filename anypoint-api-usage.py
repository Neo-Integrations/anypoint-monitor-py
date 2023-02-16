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

logger = loggingconfig.getLogger("API-USAGE-MINTOR", True)

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

            policyTemplateId = policy.get('Template ID')
            policyName = policy.get('Asset ID')
            policyStatus = policy.get('Status')
            wksUrl = False

            # jwt-policy-validation
            configuration = policy.get('Configuration')
            if policy.get('Asset ID') == 'jwt-validation':
                if len(configuration) > 0:
                    m = re.search("wksUrl:[ ]?([^ ]+)", configuration)
                    if m != None and len(m.groups()) >= 1:
                        wksUrl = m.group(1)
                        logger.info(f"wksURl => {wksUrl}");


            if policy.get('Asset ID') == None:
                config['templateId'] = policyTemplateId
                policyDetails = apimanager.policyDetails(config)
                policyName = policyDetails.get('Name')
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


def iterateOverEnvironment(config, environments, report):
    for env in environments:
        envName = env.get('Name')
        logger.info(f"Organisation=> {config['org']} Environment => {envName}")
        config['env'] = envName
        config['envId'] = env.get('Id')
        apis = apimanager.listAPIs(config)
        validateAndCollectAPILevelMetrics(config, apis, report)


def iterateOverOrganisation(config, bgs, report):
    threads = []
    for bg in bgs:
        thread = Thread(target=orgTask, args=(config, bg, report))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def orgTask(config, bg, report):
    newConfig = config.copy()
    orgName = bg.get('Name')
    logger.info(f"Business Group: {orgName}")
    newConfig['org'] = bg.get('Name')
    newConfig['orgId'] = bg.get('Id')
    environments = accessmanagement.listEnvironments(newConfig)
    iterateOverEnvironment(newConfig, environments, report)


def main():
    report = []
    logger.info("Starting ...")

    config = comlib.authConfig()
    config['logger'] = logger
    bgs = accessmanagement.listBusinessGroups(config)

    iterateOverOrganisation(config, bgs, report)
    csvhandler.writeApiValidationReport(config, report)

    logger.info("Ending ...")

    return 0


try:
    exit(main())
except Exception:
    logger.exception("Exception in main(): ")
    exit(1)