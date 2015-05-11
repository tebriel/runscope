# Runscope #

## Description ##

This utility fetches messages from the Runscope API to store into ELK.

It will fetch all the log messages since the previous run by timestamp, storing
them into the `<bucket_name>.log` file.

## Config ##

Copy the [config.json.EXAMPLE](./config.json.EXAMPLE) to `config.json` to set
up the app. You'll need to enter your runscope Key, where the log files
should go, and what buckets you'd like to fetch.

### Values ###

#### runscope_auth ####

This is your Runscope API Auth Key

#### log_dir ####

Where you'd like the app to log (make sure the app has permission!)

__Default__: `/var/log/runscope/`

#### buckets ####

A list of the Bucket IDs you'd like to get messages for.

#### last_run_path ####

The directory (relative to where you're running the app from) where to store
the last time we requested data.

__Default__: `./last_run`, relative to the path of `main.py`

## Data ##

Run logs will write to `config.json['log_dir']/run.log` and the data will be
written to `config.json['log_dir']/<bucket_key>.log`
