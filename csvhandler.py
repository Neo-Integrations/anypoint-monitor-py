import csv

def writeApiValidationReport(config, data):
    cfg = config['yamlCfg']
    headerFields = cfg['report']['validation']['header']['fields']

    with open(cfg['report']['validation']['path'], 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(headerFields)
        for each in data:
            writer.writerow(each)

def writeAPIUsageReport(config, data):
    cfg = config['yamlCfg']
    headerFields = cfg['report']['apiUsage']['header']['fields']

    with open(cfg['report']['apiUsage']['path'], 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(headerFields)
        for each in data:
            writer.writerow(each)

def writeAppUsageReport(config, data):
    cfg = config['yamlCfg']
    headerFields = cfg['report']['appUsage']['header']['fields']

    with open(cfg['report']['appUsage']['path'], 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(headerFields)
        for each in data:
            writer.writerow(each)

def writeOnPremAppUsageReport(config, data):
    cfg = config['yamlCfg']
    headerFields = cfg['report']['appUsageOnPrem']['header']['fields']

    with open(cfg['report']['appUsageOnPrem']['path'], 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(headerFields)
        for each in data:
            writer.writerow(each)


def writeEnableMonitoringReport(config, data):
    cfg = config['yamlCfg']
    headerFields = cfg['report']['enableMonitoring']['header']['fields']

    with open(cfg['report']['enableMonitoring']['path'], 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(headerFields)
        for each in data:
            writer.writerow(each)