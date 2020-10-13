# Monocle
Monocle is an exploration tool for data from the [Juno project](https://www.gbsgen.net/). It is early in development, so may be renamed and **should currently be considered unstable**.

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-brightgreen.svg)](https://github.com/sanger-pathogens/monocle/blob/master/LICENSE)  
[![Build Status](https://travis-ci.com/sanger-pathogens/monocle.svg?branch=master)](https://travis-ci.com/sanger-pathogens/monocle)  
[![codecov](https://codecov.io/gh/sanger-pathogens/monocle/branch/master/graph/badge.svg)](https://codecov.io/gh/sanger-pathogens/monocle)

UI

[![Docker Build Status](https://img.shields.io/docker/cloud/build/sangerpathogens/monocle-app.svg)](https://hub.docker.com/sangerpathogens/monocle-app)  
[![Docker Pulls](https://img.shields.io/docker/pulls/sangerpathogens/monocle-app.svg)](https://hub.docker.com/r/sangerpathogens/monocle-app)

API

[![Docker Build Status](https://img.shields.io/docker/cloud/build/sangerpathogens/monocle-api.svg)](https://hub.docker.com/r/sangerpathogens/monocle-api)  
[![Docker Pulls](https://img.shields.io/docker/pulls/sangerpathogens/monocle-api.svg)](https://hub.docker.com/r/sangerpathogens/monocle-api)

## Components
There are currently three components:
- User Interface (`ui` directory; a React application)
- GraphQL API (`api` directory; a Django+Graphene application)
- MySQL database (on a host managed by the Service Desk DBA team)

There is a further README in each directory with more detailed information.

## Production
Monocle is available internally to Sanger at the following addresses:
- `prod`: [http://monocle.pam.sanger.ac.uk/](http://monocle.pam.sanger.ac.uk/)
- `dev`: [http://monocle.dev.pam.sanger.ac.uk/](http://monocle.dev.pam.sanger.ac.uk/) (likely to be broken)

User accounts for testing functionaly are set up (with very strong passwords!) for:
- admin@sanger.ac.uk
- collaborator@globe.com

This project is early in development, so subject to change, but the current release and deploy process is described below.

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
./deploy.sh <prod|dev> <version e.g. 0.1.1> <remote user> <host address>
```

Notes:
- Although separate containers are built for UI and API components, they are currently deployed to the same OpenStack VM, running with `docker-compose`. This may change.
- There are currently deployments on OpenStack VMs in the `pathogen-dev` and `pathogen-prod` tenants.
- It is recommended to deploy to `dev`, check behaviour, then deploy to `prod`.

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

## Data
In production, the real data files are loaded from an S3 bucket, which is synced from farm5. If you have Sanger credentials, see the companion gitlab repo [monocle-farm5](https://gitlab.internal.sanger.ac.uk/sanger-pathogens/monocle-farm5).

For development and testing, lightweight mock data for a single lane is used. See the `mock-data` directory within the repo.

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
