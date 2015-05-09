# Runscope #

## Description ##

This utility fetches messages from the Runscope API to store into ELK.

It will fetch all the log messages since the previous run by timestamp, storing
them into the `<bucket_name>.log` file.

## Config ##

Copy the [config.json.EXAMPLE](./config.json.EXAMPLE) to `config.json` to set
up the app. You'll need to enter your runscope Key and where the log files
should go.

## Data ##

Run logs will write to `config.json['log_dir']/run.log` and the data will be
written to `config.json['log_dir']/data.log`
