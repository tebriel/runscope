#!/usr/bin/env python3.4

import logging
import math
import json
import argparse
from os import path
from datetime import datetime, timedelta
from runscope import Runscope


def get_last_run():
    """Gets the UNIX timestamp of the last run
    Gets now - 1 hour if no timestamp available
    """
    try:
        with open('.last_run', 'r') as last_run_file:
            last_run = last_run_file.readline().strip()
    except (OSError, IOError):
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


def save_result(config, key, result):
    """Saves the result from the latest run to the bucket data file"""
    file_name = '%s.log' % (key)
    data_file_path = path.join(config['log_dir'], file_name)
    with open(data_file_path, 'a') as data:
        data.write("%s\n" % (json.dumps(result)))


def load_config(config_path):
    """Loads our config from the config file"""
    with open(config_path) as config_file:
        config = json.load(config_file)
    return config


def configure_logging(config):
    """Sets up our logging settings"""
    logfile = path.join(config['log_dir'], 'run.log')
    logging.basicConfig(filename=logfile, level=getattr(logging, 'DEBUG'))


def get_runscope_data(config, last_run):
    """Fetches all our runscope data we want"""
    rs = Runscope(config['runscope_auth'])
    for bucket in config['buckets']:
        result = rs.get_bucket_messages(bucket, since=last_run)
        message = 'Fetched Bucket: %s with %d messages'
        logging.debug(message, bucket, len(result))
        save_result(config, bucket, result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='runscope',
                                     description='Runscope Message Fetcher')

    parser.add_argument('-f')
    args = parser.parse_args()
    config = load_config(args.f)
    configure_logging(config)

    last_run = get_last_run()
    get_runscope_data(config, last_run)

    save_last_run(math.floor(datetime.now().timestamp()))
