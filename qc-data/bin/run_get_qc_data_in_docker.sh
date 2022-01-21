#!/usr/bin/env bash

# This runs `get_qc_data.py`, for Streptococcus agalactiae, followed
# by update_qc_data_db_table.py.    These are run within a
# `monocle-dash-api` container in order to provide access to the APIs.
# 
# Using the -u option ensures that file/directories are owned by the
# application user rather than root.
# 
# Volume mounts required are:
# - the s3 bucket (source data) directory as SAMPLE_DATA_PATH
# - the output directory as `/app/monocle_pipeline_qc`
# - the db config file as `/app/my.cnf`
# - the MLWH API config file as `/app/mlwh-api.yml`
# - ./qc-data in `/app/qc-data`
# 
# Network:
# - must be attached to the Monocle docker network (see `docker-compose.yml`);
#   docker compose names this after the user that starts it
# 
# The s3 bucket is mounted as SAMPLE_DATA_PATH to that target of the symlinks
# has the same path within the container as on the host machine.

SAMPLE_DATA_PATH="${HOME}/monocle_juno"
OUTPUT_DIR="${HOME}/monocle_juno_pipeline_qc"
docker run  -u `id -u`:`id -g` \
         --rm \
         --volume  ${SAMPLE_DATA_PATH}:${SAMPLE_DATA_PATH}  \
         --volume  ${OUTPUT_DIR}:/app/monocle_pipeline_qc \
         --volume  `pwd`/my.cnf:/app/my.cnf \
         --volume  `pwd`/mlwh-api.yml:/app/mlwh-api.yml \
         --volume  `pwd`/qc-data:/app/qc-data \
         --env     "MONOCLE_DATA=/home/<USER>/monocle_juno" \
         --env     "PYTHONPATH=/app:/app/qc-data" \
         --network <USER>_default \
         --name "get_qc_data_$$" \
         gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/monocle-dash-api:<DOCKERTAG> \
         bash -c "python3 ./qc-data/bin/get_qc_data.py --species 'Streptococcus agalactiae' && python3 ./qc-data/bin/update_qc_data_db_table.py"
