# End-to-end tests
This directory contains end-to-end tests written using [cypress](https://www.cypress.io/).

## Usage
To run the tests:
```
docker-compose up --exit-code-from cypress
```

The output will be generated in the `cypress` directory and contains a video of the tests and screenshots of error cases, if any exist.

To add a test, edit the files in the `integration` directory.