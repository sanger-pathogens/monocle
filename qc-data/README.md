# QC Data Service

## Running unit tests in situ

```
cd monocle
cd dash-api/juno; docker build --rm -t dash-api:test .; cd ../../; docker run -v `pwd`/qc-data:/app/qc-data -v `pwd`/qc-data/unittests.sh:/app/unittests.sh -it --rm dash-api:test /app/unittests.sh
```
