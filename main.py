#!/usr/bin/env python3

import logging
import math
import json
from os import path
from datetime import datetime, timedelta
from runscope import Runscope


def get_last_run():
    """Gets the UNIX timestamp of the last run"""
    try:
        with open('.last_run', 'r') as last_run_file:
            last_run = last_run_file.readline().strip()
    except OSError:
        logging.warn('.last_run is missing, will recreate')
        last_run = ''

    if last_run == '':
        # Just get the last hour if we don't have an original run
        last_run = datetime.now() - timedelta(hours=1)
    else:
        # Else we'll just get the data since the last time we ran
        last_run = datetime.fromtimestamp(int(last_run))
    last_run = math.floor(last_run.timestamp())
    logging.debug('Set last_run as %d', last_run)
    return last_run


def save_last_run(last_run):
    """Saves the UNIX timestamp of the current run"""
    with open('.last_run', 'w') as last_run_file:
        last_run_file.write('%d' % (last_run))

    logging.debug('Saved last_run as %d', last_run)


def save_result(config, result):
    data_file_path = path.join(config['log_dir'], 'data.log')
    with open(data_file_path, 'a') as data:
        data.write("%s\n" % (json.dumps(result)))


def load_config():
    with open('config.json') as config_file:
        config = json.load(config_file)
    return config


def configure_logging(config):
    logfile = path.join(config['log_dir'], 'run.log')
    logging.basicConfig(filename=logfile, level=getattr(logging, 'DEBUG'))


def get_runscope_data(config, last_run):
    rs = Runscope(config['runscope_auth'])
    result = {}
    buckets = rs.get_buckets()
    for bucket in buckets:
        if bucket['name'] == 'PRS API':
            result[bucket['name']] = rs.get_bucket_messages(bucket['key'],
                                                            since=last_run)
            message = 'Found Bucket: %s with %d messages'
            logging.debug(message, bucket['name'], len(result[bucket['name']]))
    save_result(config, result['PRS API'])


if __name__ == '__main__':
    config = load_config()
    configure_logging(config)

    last_run = get_last_run()
    get_runscope_data(config, last_run)

    save_last_run(math.floor(datetime.now().timestamp()))
