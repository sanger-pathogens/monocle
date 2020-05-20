# Monocle
Monocle is an exploration tool for data from the [Juno project](https://www.gbsgen.net/). It is early in development, so may be renamed and **should currently be considered unstable**.

## Components
There are currently two components:
- User Interface (`ui` directory; a React application)
- GraphQL API (`api` directory; a Django+Graphene application with mock data in SQLite3)

There is a further README in each directory with more detailed information.

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
