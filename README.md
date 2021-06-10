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

Wait until the `docker_build` and `docker_push` stages of ther CI pipeline have completed.

#### Deploying a release

Run:
```
./deploy.sh -e <prod|dev> -v <version e.g. 0.1.1> -m <yes|no> -u <remote user> -h <host address>
```

Notes:
- Using <b>-m yes</b> will also run any release Django database migrations
- There are currently deployments on OpenStack VMs in the `pathogen-dev` and `pathogen-prod` tenants.
- It is recommended to deploy to `dev`, check behaviour, then deploy to `prod`.

#### Test deployments

- `prod` deployments _must_ always be releases (as above).  Anything that includes a database migration
should also be a release.
- `dev` deployments _could_ be a release or _could_ be from the current head of the master branch.

It is often useful to deploy the the current head of the master branch, e.g. right after a merge,
to test it but prior to making a release.

Run:
```
./deploy.sh -e dev -m no -u <remote user> -h <host address> --branch master --tag unstable
```

This will deploy the current head of the master branch, and the docker images built from it
(`--tag` is a _docker_ tag, not a git tag).

#### Test deployments on personal development instances

Test deployments to `dev` (as above) should only be a release or the head of the master branch, but
you may want to deploy a feature branch you are working on to your own development instance.

Run:
```
./deploy.sh -e dev -m no -u <remote user> -h <host address> --branch <feature_branch> --tag commit-$(git rev-parse --short=8 HEAD)
```
You can name any branch and any docker tag you like; you almost certainly want the docker tag
for your latest commit (as in the example above).  The CI pipelines will build images for every commit, with the prefix `commit-`
followed by the short commit SHA (8 chars in gitlab).   Currently `deploy.sh` will deploy to the designated users' home
directory, so you will want to create a new user on your development box.


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
