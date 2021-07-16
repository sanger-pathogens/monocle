# Dashboard API
This component provides an API for accessing data required by the frontend dashboard UI.

## Building a local Docker image
A local docker image can be built using the following:
```
cd metadata/juno
docker build --rm -t dash-api:test .
```

## Running unit tests in situ
Use the following:
```
cd monocle
docker run -it --rm dash-api:test /app/unittests.sh
```

## Running up
The service can be run locally outside of compose using the following:
```
cd monocle
docker run -p80:80 -it --rm -e "ENABLE_SWAGGER_UI=true" dash-api:test
```

# Testing
If you need to run up a swagger UI for testing then set the ENABLE_SWAGGER_UI environment variable to *true* when running up the container [as above].
The swagger UI can then be accessed on:
```
http://0.0.0.0/ui/
```

# Adding a new endpoint
Follow these steps:
* Define the endpoint input/output schema in the *api/interface/openapi.yml* definition file.
* Create a handler method in the *api/routes.py* module. The *operationId* property in the open api definition should point at the handler method [with full package path].
* Currently routes handler methods access backend code for the ServiceFactory class.
* Test the endpoint using Swagger UI as above.
