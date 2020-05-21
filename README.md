# Monocle
Monocle is an exploration tool for data from the [Juno project](https://www.gbsgen.net/). It is early in development, so may be renamed and **should currently be considered unstable**.

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
docker-compose up
```

It should then be possible to run commands on subcomponents with:
```
docker-compose run <subcomponent> <command>
```

### Development directly on your development machine
This requires a bit more setup, but may be easier to debug. Also, editor integration such as python linting/autocomplete may be easier to set up. Read about setting up the [ui](ui/README.md) and [api](api/README.md) separately.
