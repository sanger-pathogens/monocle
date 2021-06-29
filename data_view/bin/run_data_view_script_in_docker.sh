#!/usr/bin/bash

# This runs `create_download_view_for_sample_data.py` inside a `monocle-dash` container
# 
# Volume mounts required are:
# - the s3 bucket (source data) directory as `/dash/data`
# - the output directory as `/dash/data_view`
# - the db config file as `/dash/my.cnf`
# - the script itself, in `/dash`

docker run  --volume `pwd`/monocle_juno:/dash/data  \
            --volume `pwd`/data_view:/dash/data_view  \
            --volume `pwd`/my.cnf:/dash/my.cnf \
            --volume `pwd`/create_download_view_for_sample_data.py:/dash/create_download_view_for_sample_data.py \
            gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/monocle-dash:<DOCKERTAG> \
            python3 ./create_download_view_for_sample_data.py
