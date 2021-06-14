# Monocle
Monocle is an exploration tool for data from the [Juno project](https://www.gbsgen.net/). It is early in development, so may be renamed and **should currently be considered unstable**.

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-brightgreen.svg)](https://github.com/sanger-pathogens/monocle/blob/master/LICENSE)  
[![codecov](https://codecov.io/gh/sanger-pathogens/monocle/branch/master/graph/badge.svg)](https://codecov.io/gh/sanger-pathogens/monocle)

UI

[![Docker Repository on Quay](https://quay.io/repository/sangerpathogens/monocle-app/status "Docker Repository on Quay")](https://quay.io/repository/sangerpathogens/monocle-app)

API

[![Docker Repository on Quay](https://quay.io/repository/sangerpathogens/monocle-api/status "Docker Repository on Quay")](https://quay.io/repository/sangerpathogens/monocle-api)

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

### Deployment
Wait until the docker_build and docker_push stages of the CI pipeline have completed.

### Deploying a release
Run:
```
./deploy.sh -e <prod|dev> -v <version e.g. 0.1.1> -u <remote user> -h <host address>
```

Notes:
- Several release *modes* are allowed:
  - If the deployment includes a database release as well as code, then use the `-m all` argument.
  - If only a database release is required then use the `-m database` argument.
  - The default is a code release only [`-m application`].
- There are currently deployments on OpenStack VMs in the `pathogen-dev` and `pathogen-prod` tenants.
- It is recommended to deploy to `dev`, check behaviour, then deploy to `prod`.

#### Database release requirements
If database changes are to be deployed, then the following is required:
- A locally installed mysql client on the deployment machine.
- Release SQL should be defined in a `database/releases/<version>/release.sql` file.
- An additional `-c <path to connection file>` argument must be passed to the deploy.sh script. The connection file will hold the connection details for the database instance to be updated.

## Development

### Setup
Read about setting up the [ui](ui/README.md) and [api](api/README.md) separately.

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
