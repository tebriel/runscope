#!/usr/bin/env python3.4

import logging
import math
import json
import argparse
import fcntl
from os import path
from datetime import datetime, timedelta
from runscope import Runscope


def get_last_run(config):
    """Gets the UNIX timestamp of the last run
    Gets now - 1 hour if no timestamp available
    """
    try:
        with open(config['last_run_path'], 'r') as last_run_file:
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


def save_last_run(last_run, config):
    """Saves the UNIX timestamp of the current run"""
    with open(config['last_run_path'], 'w') as last_run_file:
        last_run_file.write('%d' % (last_run))

    logging.debug('Saved last_run as %d', last_run)


def save_result(config, key, result):
    """Saves the result from the latest run to the bucket data file"""
    file_name = '%s.log' % (key)
    data_file_path = path.join(config['log_dir'], file_name)
    with open(data_file_path, 'a') as data:
        fcntl.flock(data, fcntl.LOCK_EX)
        data.write("%s\n" % (json.dumps(result)))
        fcntl.flock(data, fcntl.LOCK_UN)


def load_config(config_path):
    """Loads our config from the config file"""
    cwd = path.dirname(path.realpath(__file__))
    if config_path is None:
        config_path = path.join(cwd, 'config.json')
    with open(config_path) as config_file:
        config = json.load(config_file)

    # Default for Last Run
    if config.get('last_run_path') is None:
        config['last_run_path'] = path.join(cwd, '.last_run')

    # Default for Log Dir
    if config.get('log_dir') is None:
        config['log_dir'] = '/var/log/runscope'

    return config


def configure_logging(config):
    """Sets up our logging settings"""
    logfile = path.join(config['log_dir'], 'run.log')
    logging.basicConfig(filename=logfile, level=getattr(logging, 'DEBUG'))


def get_runscope_data(config, last_run, stdout):
    """Fetches all our runscope data we want"""
    success = True
    rs = Runscope(config['runscope_auth'])
    for bucket in config['buckets']:
        result = rs.get_bucket_messages(bucket, since=last_run, count=999)
        message = 'Fetched Bucket: %s with %d messages'
        if result is None:
            logging.error('No messages came back')
            success = False
            continue
        logging.debug(message, bucket, len(result))
        if stdout:
            print(json.dumps(result))
        else:
            save_result(config, bucket, result)
    return success


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='runscope',
                                     description='Runscope Message Fetcher')

    parser.add_argument('-f')
    parser.add_argument('--stdout', action='store_true')
    args = parser.parse_args()
    config = load_config(args.f)
    configure_logging(config)

    last_run = get_last_run(config)
    get_success = get_runscope_data(config, last_run, args.stdout)

    if get_success:
        save_last_run(math.floor(datetime.now().timestamp()), config)
