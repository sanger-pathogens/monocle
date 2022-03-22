# QC Data Service



## Running unit tests in situ

The unit tests need to be run inside a dash-api container.  The `latest` version can be used
provided this branch does not require any dash-api chnages that have been made since the latest release.

If you need a more recent docker image from this branch, use `TAG="commit-"$(git rev-parse --short=8 HEAD)`
(remember you will need to push the commit and wait for the pipeline to build the image).

```
TAG="latest"
IMAGE="gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/monocle-dash-api:${TAG}"
docker pull "$IMAGE"
docker run -it --rm  \
           --volume `pwd`:/app/qc-data \
           --volume `pwd`/unittests.sh:/app/unittests.sh \
           "$IMAGE" \
           bash -c "/app/unittests.sh && cd qc-data && coverage report"
```


## Running the get_qc_data.py script

The script can be run in a dash-api container (as with unit tests: see note above).

- API queries need to be made, a Monocle service must be running.
- The `--network` option attaches the container to the Monocle service docker
  network, making the APIs accessible.
- The `--volume` options make the qc-data code, config files and kraken reports
  available in the container; and mount he output directory on the host
  so the QC data files are available.
- The `--env` option sets MONOCLE_DATA in the container environment, which
  is where the kraken_report directory has been mounted in the container.
- The `--user` option will run the container as the user that starts it, so
  the output files are owned by that user rather than by root.

This can be run from outside the qc-data directory, but host path used to volume
mount `/app/qc-data` will need to be altered accordingly. 
  
```
TAG="latest"
IMAGE="gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/monocle-dash-api:${TAG}"
docker pull "$IMAGE"
docker run -it --rm \
           --user    `id -u`:`id -g` \
           --volume  `pwd`:/app/qc-data \
           --volume  `pwd`/monocle_juno:/home/monocle/monocle_juno \
           --volume  `pwd`/my.cnf:/app/my.cnf \
           --volume  `pwd`/mlwh-api.yml:/app/mlwh-api.yml \
           --volume  `pwd`/monocle_pipeline_qc:/app/monocle_pipeline_qc \
           --env     "MONOCLE_DATA=/home/monocle/monocle_juno" \
           --env     "PYTHONPATH=/app:/app/qc-data" \
           --network monocle_default \
           "$IMAGE" \
           bash -c "python3 ./qc-data/bin/get_qc_data.py"
```

## Running the update_qc_data_db_table.py script 

This is essentially the same as running `get_qc_data.py`, though some of options used
with that script are not needed in this case:

```
TAG="latest"
IMAGE="gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/monocle-dash-api:${TAG}"
docker pull "$IMAGE"
docker run -it --rm \
           --user    `id -u`:`id -g` \
           --volume  `pwd`:/app/qc-data \
           --volume  `pwd`/monocle_pipeline_qc:/app/monocle_pipeline_qc \
           --env     "PYTHONPATH=/app:/app/qc-data" \
           --network monocle_default \
           "$IMAGE" \
           bash -c "python3 ./qc-data/bin/update_qc_data_db_table.py"
```
