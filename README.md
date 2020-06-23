# Monocle
Monocle is an exploration tool for data from the [Juno project](https://www.gbsgen.net/). It is early in development, so may be renamed and **should currently be considered unstable**.

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-brightgreen.svg)](https://github.com/sanger-pathogens/monocle/blob/master/LICENSE)  
[![Build Status](https://travis-ci.org/sanger-pathogens/monocle.svg?branch=master)](https://travis-ci.org/sanger-pathogens/monocle)  
[![codecov](https://codecov.io/gh/sanger-pathogens/monocle/branch/master/graph/badge.svg)](https://codecov.io/gh/sanger-pathogens/monocle) 

UI

[![Docker Build Status](https://img.shields.io/docker/cloud/build/sangerpathogens/monocle-app.svg)](https://hub.docker.com/sangerpathogens/monocle-app)  
[![Docker Pulls](https://img.shields.io/docker/pulls/sangerpathogens/monocle-app.svg)](https://hub.docker.com/r/sangerpathogens/monocle-app)

API

[![Docker Build Status](https://img.shields.io/docker/cloud/build/sangerpathogens/monocle-api.svg)](https://hub.docker.com/r/sangerpathogens/monocle-api)  
[![Docker Pulls](https://img.shields.io/docker/pulls/sangerpathogens/monocle-api.svg)](https://hub.docker.com/r/sangerpathogens/monocle-api)

## Components
There are currently two components:
- User Interface (`ui` directory; a React application)
- GraphQL API (`api` directory; a Django+Graphene application with mock data in SQLite3)

There is a further README in each directory with more detailed information.

## Production
This is early in development, so subject to change, but the current process is described below.

### Making a release
Currently, to make a release, make sure you are on the `master` branch with nothing to commit, then run:
```
./release.sh <version>
```
Note: `<version>` should conform to [semver](https://semver.org/).

### Deploying a release
Wait until [Docker hub](https://hub.docker.com/orgs/sangerpathogens) has built the images for the release. These are named:
- `sangerpathogens/monocle-api:<version>`
- `sangerpathogens/monocle-app:<version>`

Now run:
```
./deploy.sh <version>
```

Notes:
- Although separate containers are built for UI and API components, they are currently deployed to the same OpenStack VM, running with `docker-compose`. This may change.
- There is currently only an OpenStack VM in the `pathogen-dev` tenant. A similar one will be set up in `pathogen-prod` when things are more stable.

## Development
There are two supported ways to set up a development environment:
- using `docker-compose`
- installing dependencies locally and running directly on your development machine

### Development with `docker-compose`
If you have `docker` installed, run:
```
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up
```

It should then be possible to run commands on subcomponents with:
```
docker-compose -f docker-compose.dev.yml run <subcomponent> <command>
```

### Development directly on your development machine
This requires a bit more setup, but may be easier to debug. Also, editor integration such as python linting/autocomplete may be easier to set up. Read about setting up the [ui](ui/README.md) and [api](api/README.md) separately.

## Mock data
**Note: This section is temporary and is intended to be removed.**

For development of the download functionality, please load the following sample lane.
```
scp -r <you>@pcs6:/lustre/scratch118/infgen/pathogen/pathpipe/prokaryotes/seq-pipelines/Streptococcus/agalactiae/TRACKING/5903/5903STDY8059170/SLX/23800977/31663_7#113 ./mock-data/
```

For the OpenStack instance, transfer this from your machine to the instance. This should only need to be done once after the instance is created.
```
scp -r ./mock-data pathpipe@monocle.dev.pam.sanger.ac.uk:~/mock-data
```

## Testing
There are currently:
- integration tests in the `e2e` directory
- unit tests in the `api` directory

To run the integration tests, add [cypress](https://www.cypress.io/) with `yarn global add cypress` (first time only), then run:
```
# build images
docker-compose -f docker-compose.e2e.yml up --build -d

# run (in e2e dir as cypress root)
cd e2e
cypress run
```

Further information on each can be found in the relevant directory.
