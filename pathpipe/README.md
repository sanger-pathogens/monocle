# pathpipe files

This directory contains files that should be installed by `pathpipe` on farm5.


# crontab

A crontab entry that runs the `juno_pipeline_status.sh` script.

# `bin`

## `juno_pipeline_status.sh`

Uses `pf` to get pipeline status for JUNO lanes.  Writes the status data to a
CSV file which is then copied to an OpenStack instance running the Monocle service.

**Important:** this uses an SSH identity which must be provided with access to
the user account running the Monocle service on the OpenStack instance.  Enter
the public ssh key in `$HOME/.ssh/authorized_keys` and prefix it with
`from="172.27.71.115",restrict ` so that the key may only be used to push data
to the instance (the IP address should be the host on which the `pathpipe` cron
job is run).
