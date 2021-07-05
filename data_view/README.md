# Folder view for downloading sample data

`./bin/create_download_view_for_sample_data.py` creates a folder for each lane of each institution w/ symlinks to sample data files.

The script is meant to be run on the server: `./sync_data_view_cron` creates a Docker container w/ the required environment and runs the script inside the container.

Both the script and the cron file are deployed to the server by `deploy.sh`.

## Tests

The unit tests of the script are loccated in `./tests`. They are run by the CI pipeline.
