import logging
import yaml

def getLogger(loggerName, createFile=False):
        with open('../resources/config-dev.yaml', 'r') as f:
                cfg = yaml.load(f, Loader=yaml.SafeLoader)
        
        consoleLongLevel = logging._nameToLevel[cfg["log"]["flevel"]]
        fileLogLevel = logging._nameToLevel[cfg["log"]["flevel"]]

        log = logging.getLogger(loggerName)
        log.setLevel(level=consoleLongLevel)

        formatter = logging.Formatter(cfg["log"]["formatter"])

        if createFile:
                fh = logging.FileHandler(cfg["log"]["filePath"])
                fh.setLevel(level=fileLogLevel)
                fh.setFormatter(formatter)

        # reate console handler for logger.
        ch = logging.StreamHandler()
        ch.setLevel(level=consoleLongLevel)
        ch.setFormatter(formatter)

        # add handlers to logger.
        if createFile:
            log.addHandler(fh)

        log.addHandler(ch)
        
        return  log