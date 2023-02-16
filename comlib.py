import os
import yaml
import json
import accessmanagement
import logging
import loggingconfig

# This method will return the prefix of the anypoint-cli command.
# The prefix will include, all the credentials, - 
# organisation and environment details
def anypointCliCmdPrefix(config):

    logger = config['logger']
    token = {}
    if config.get('access_token') == None:
        token  = accessmanagement.getToken(config)
        # token = {"access_token":"43846673-8339-49e5-bb11-a8ad1e31e472"}
        config['access_token'] = token
    else:
        token = config['access_token']
    
    cmd = ["anypoint-cli"]
    cmd.append("--bearer")
    cmd.append(f"{token['access_token']}")
    if config.get('org') != None:
        cmd.append("--organization")
        cmd.append(f"{config['org']}")
    
    if config.get('env') != None:
        cmd.append("--environment")
        cmd.append(f"{config['env']}")

    return cmd


def authConfig():

    logger = loggingconfig.getLogger("AUTH-CONFIG", True)

    with open('../resources/config-dev.yaml', 'r') as f:
        cfg = yaml.load(f, Loader=yaml.SafeLoader)

    authStrategy = cfg["auth"]["strategy"]
    config = dict()
    config['yamlCfg'] = cfg

    if authStrategy == "userPassword":
        username = os.environ.get("ANYPOINT_USERNAME")
        password = os.environ.get("ANYPOINT_PASSWORD")
        config['username']=  username
        config['password'] = password

    elif authStrategy == "connectedApp":
        clientId = os.environ.get("ANYPOINT_CLIENT_ID")
        clientSecret = os.environ.get("ANYPOINT_CLIENT_SECRET")
        config['clientId']=  clientId
        config['clientSecret'] = clientSecret

    elif authStrategy == "refreshToken":
        clientId = os.environ.get("ANYPOINT_CLIENT_ID")
        clientSecret = os.environ.get("ANYPOINT_CLIENT_SECRET")
        refreshToken = os.environ.get("ANYPOINT_REFRESH_TOKEN")
        config['clientId']=  clientId
        config['clientSecret'] = clientSecret
        config['refreshToken'] = refreshToken

    config['authStrategy'] = authStrategy

    logger.debug(f"{config}");
    
    return config
    


