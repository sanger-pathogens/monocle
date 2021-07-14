#!/usr/bin/env bash

# This runs `create_download_view_for_sample_data.py` inside a `monocle-dash` container
# 
# Volume mounts required are:
# - the s3 bucket (source data) directory as `/dash/monocle_juno`
# - the s3 bucket (source data) directory as SAMPLE_DATA_PATH
# - the output directory as `/dash/monocle_juno_institution_view`
# - the db config file as `/dash/my.cnf`
# - the MLWH API config file as `/dash/mlwh-api.yml`
# - the script itself, in `/dash`
# 
# The s3 bucket is mounted as SAMPLE_DATA_PATH to that target of the symlinks
# has the same path within the container as on the host machine.
# 
# Any arguments provided will be passed to the script

SAMPLE_DATA_PATH="${HOME}/monocle_juno"

docker run  --volume ${SAMPLE_DATA_PATH}:${SAMPLE_DATA_PATH}  \
            --volume `pwd`/monocle_juno_institution_view:/dash/monocle_juno_institution_view  \
            --volume `pwd`/my.cnf:/dash/my.cnf \
            --volume `pwd`/mlwh-api.yml:/dash/mlwh-api.yml \
            --volume `pwd`/create_download_view_for_sample_data.py:/dash/create_download_view_for_sample_data.py \
            gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/monocle-dash:<DOCKERTAG> \
            python3 ./create_download_view_for_sample_data.py --data_dir "$SAMPLE_DATA_PATH" $@ 
