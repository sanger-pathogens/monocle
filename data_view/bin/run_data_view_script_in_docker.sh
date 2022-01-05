#!/usr/bin/env bash

# This runs `create_download_view_for_sample_data.py` inside a `monocle-dash-api` container
# 
# Volume mounts required are:
# - the s3 bucket (source data) directory as SAMPLE_DATA_PATH
# - the output directory as `/app/monocle_juno_institution_view`
# - the db config file as `/app/my.cnf`
# - the MLWH API config file as `/app/mlwh-api.yml`
# - the script itself, in `/app`
# 
# Network:
# - must be attached to the Monocle docker network (see `docker-compose.yml`);
#   docker compose names this after the user that starts it
# 
# The s3 bucket is mounted as SAMPLE_DATA_PATH to that target of the symlinks
# has the same path within the container as on the host machine.
# 
# Any arguments provided will be passed to the script

SAMPLE_DATA_PATH="${HOME}/monocle_juno"

# Using the -u option ensures that file/directories are owned by the application user rather than root
if ! docker run  -u `id -u`:`id -g` \
            --rm \
            --volume ${SAMPLE_DATA_PATH}:${SAMPLE_DATA_PATH}  \
            --volume `pwd`/monocle_juno_institution_view:/app/monocle_juno_institution_view  \
            --volume `pwd`/my.cnf:/app/my.cnf \
            --volume `pwd`/mlwh-api.yml:/app/mlwh-api.yml \
            --volume `pwd`/create_download_view_for_sample_data.py:/app/create_download_view_for_sample_data.py \
            --env "MONOCLE_DATA=/home/<USER>/monocle_juno" \
            --name "create_download_view_for_sample_data_$$" \
            --network <USER>_default \
            gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/monocle-dash-api:<DOCKERTAG> \
            python3 ./create_download_view_for_sample_data.py --data_dir "$SAMPLE_DATA_PATH" $@
then
  exit 255
fi

# Add md5 checksum files to each lane after all the directories have been created.
# Doing this here should ensure that any new lanes/data get md5 files added asap.
# If this step proves too slow, we may need to consider moving it to separate cron entry
# or changing the job frequency.
MD5_ROOT_DIR="${HOME}/monocle_juno_institution_view"
for DIR in $(find "$MD5_ROOT_DIR" -follow -mindepth 2 -maxdepth 2 -type d -not -path "${MD5_ROOT_DIR}/downloads" 2>&1 | grep -v '/downloads.: Permission denied')
do
   cd "${DIR}"
   if ls * > /dev/null 2>&1
   then
      md5sum $(ls * | grep -v '\.md5$') >$(basename "${DIR}").md5
   fi
done
