# QC Data Service

## Running unit tests in situ

```
cd dash-api/juno
docker build --rm -t dash-api:test .
cd ../../
docker run -v `pwd`/qc-data:/app/qc-data -v `pwd`/qc-data/unittests.sh:/app/unittests.sh -it --rm dash-api:test /app/unittests.sh
```


## Running the get_qc_data.py script

The script can be run in a dash-api container.

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

```
docker run -it --rm \
           --user    `id -u`:`id -g` \
           --volume  `pwd`/qc-data:/app/qc-data \
           --volume  `pwd`/monocle_juno:/home/monocle/monocle_juno \
           --volume  `pwd`/my.cnf:/app/my.cnf \
           --volume  `pwd`/mlwh-api.yml:/app/mlwh-api.yml \
           --volume  `pwd`/monocle_pipeline_qc:/app/monocle_pipeline_qc \
           --env     "MONOCLE_DATA=/home/monocle/monocle_juno" \
           --env     "PYTHONPATH=/app:/app/qc-data" \
           --network monocle_default dash-api:test \
           bash -c "python3 ./qc-data/bin/get_qc_data.py"
```
