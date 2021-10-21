# Folder view for downloading sample data

`./bin/create_download_view_for_sample_data.py` creates a folder for each lane of each institution w/ symlinks to sample data files.

The script `./bin/run_data_view_script_in_docker.sh` runs the dash-api container w/ the required environment and runs the python script inside the container. This is scheduled in monocle_crontab in monocle-box in fce-management.

Both the scripts are deployed to the server by `deploy.sh`.

## Tests

The unit tests of the script are loccated in `./tests`. They are run by the CI pipeline.
