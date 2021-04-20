# Metadata API
This component provides an API for accessing and updating metadata in the Monocle database.

## Running up
The service can be run locally outside of compose using the following command:
```
cd monocle
docker run -v `pwd`/metadata/juno/my.cnf:/app/my.cnf -v `pwd`/metadata/juno/config.json:/app/config.json -p3001:80 -it --rm metadata-api:test
```

# Testing
The service provides a swagger UI which can be accessed on:
```
http://0.0.0.0:3001/metadata/ui/
```
