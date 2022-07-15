#!/usr/bin/env bash

# This runs `create_download_view_for_sample_data.py` inside a
# `monocle-dash-api` container.  Using the -u option ensures that
# file/directories are owned by the application user rather than root.
# 
# Volume mounts required are:
# - the s3 bucket (source data) directory as SAMPLE_DATA_PATH
# - the output ("insttitution view") directory as `/app/${INST_VIEW_SUBDIR}`
# - the db config file as `/app/my.cnf`
# - the MLWH API config file as `/app/mlwh-api.yml`
# - the script itself, in `/app`
# 
# Network:
# - must be attached to the Monocle docker network (see `docker-compose.yml`);
#   docker compose names this after the user that starts it
# 
# The s3 bucket is mounted as SAMPLE_DATA_PATH so that target of the symlinks
# has the same path within the container as on the host machine.
# 
# Any arguments provided will be passed to the script

SAMPLE_DATA_SUBDIR="monocle_juno"
SAMPLE_DATA_PATH="${HOME}/${SAMPLE_DATA_SUBDIR}"
INST_VIEW_SUBDIR="monocle_juno_institution_view"
INST_VIEW_PATH="${HOME}/${INST_VIEW_SUBDIR}"
if ! docker run  -u `id -u`:`id -g` \
            --rm \
            --volume ${SAMPLE_DATA_PATH}:/home/<USER>/${SAMPLE_DATA_SUBDIR}  \
            --volume ${INST_VIEW_PATH}:/app/${INST_VIEW_SUBDIR}  \
            --volume `pwd`/my.cnf:/app/my.cnf \
            --volume `pwd`/mlwh-api.yml:/app/mlwh-api.yml \
            --volume `pwd`/create_download_view_for_sample_data.py:/app/create_download_view_for_sample_data.py \
            --env "MONOCLE_DATA=/home/<USER>/${SAMPLE_DATA_SUBDIR}" \
            --name "create_download_view_for_sample_data_$$" \
            --network <USER>_default \
            gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/monocle-dash-api:<DOCKERTAG> \
            python3 ./create_download_view_for_sample_data.py --data_dir "$SAMPLE_DATA_PATH" $@
then
  exit 255
fi



# Add MD5 checksum files to each lane after all the directories have been
# created.   Doing this here should ensure that any new lanes/data get MD5
# checksum files added asap.
MD5_ROOT_DIR="${INST_VIEW_PATH}"
DOWNLOADS_DIR="${MD5_ROOT_DIR}/downloads"
# be careful with this for loop:  DIR may include a space so patterns like
# `for DIR $(ls pattern | some | pipe)` won't work as expected
for DIR in ${MD5_ROOT_DIR}/*/*/
do

   # don't attempt to look in the downloads directory
   if [[ $DIR == *"${DOWNLOADS_DIR}"* ]]
   then
      continue
   fi
   
   # create MD5 checksum files in all other directories...
   if cd "${DIR}"
   then
   
      # ...assuming the directory has some files in it 
      if ls * > /dev/null 2>&1
      then
      
         DATA_FILES=$(ls * | grep -v '\.md5$')
         MD5_FILE=$(basename "$DIR").md5
         
         # See if there are any files newer than the MD5 checksum file.  Note
         # NEW_DATA will also be true if the MD5 checksum file has not yet
         # been created.
         NEW_DATA=false
         for FILE in $(echo $DATA_FILES)
         do
            if [ "$FILE" -nt "$MD5_FILE" ]
            then
               NEW_DATA=true
            fi
         done
         
         # create new MD5 checksum file if there are new data files
         if $NEW_DATA
         then
            md5sum $(echo $DATA_FILES) > "$MD5_FILE"
         fi
         
      fi # if ls  ...
      
   else # if cd ...
   
      echo "Cannot CWD to ${DIR}: no MD5 checksum file will be created here."
      
   fi # if cd ...
   
done
