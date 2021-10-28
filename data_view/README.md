# Folder view for downloading sample data

`./bin/create_download_view_for_sample_data.py` creates a folder for each lane of each institution w/ symlinks to sample data files.

The script `./bin/run_data_view_script_in_docker.sh` runs in a standalone dash-api container, which provides the required environment. Note this container must be attached to the Monocle service docker network so that the metadata API can be queried.  This is scheduled by cron (the crontab is kept under version control in monocle-box in fce-management).

Both the scripts are deployed to the server by `deploy.sh`.

## Tests

The unit tests of the script are loccated in `./tests`. They are run by the CI pipeline.
