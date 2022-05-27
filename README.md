# Monocle
Monocle is an exploration tool for data from the [Juno project](https://www.gbsgen.net/). It is early in development, so may be renamed and **should currently be considered unstable**.

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-brightgreen.svg)](https://github.com/sanger-pathogens/monocle/blob/master/LICENSE)
[![coverage report](https://gitlab.internal.sanger.ac.uk/sanger-pathogens/monocle/badges/master/coverage.svg)](https://gitlab.internal.sanger.ac.uk/sanger-pathogens/monocle/-/commits/master)

[[_TOC_]]

## Components
The components include:

- An NGINX proxy server
- User Interface (`frontend` directory; a _Svelte_ application)
- OpenAPI web services (`dash-api` directory; a Python _Connexion_ application)
- OpenLDAP service
- MySQL database (on a host managed by the Service Desk DBA team)

There is a further README in each directory with more detailed information.

## Development

### Prerequisites

#### Pre-commit hooks

Monocle's pre-commit hooks (speficied in `./.pre-commit-config.yaml`) are run before each commit automatically. We use them to auto-format code and to check for linting errors, for example. W/o running the hooks, the CI pipeline may fail.

First, install [`pre-commit`](https://pre-commit.com/#installation) command itself if you don't have it already:
```
pip install pre-commit
```
##### Python3.8 and virtualenv module

Python 3.8._n_ is required for pre-commit (see below).   This should provide a `python3.8` executable that runs whatever 3.8._n_ you have installed.

The virtualenv module is used internally by pre-commit; if not installed, run `pip install virtualenv`.

Then, run `pre-commit install` from the repository's folder to install the pre-commit hooks.

##### Running pre-commit hooks manually

First, install [`pre-commit`](https://pre-commit.com/#installation) command itself if you don't have it already:
```
pip install pre-commit
```

Then, run `pre-commit install` from the repository's folder to install the pre-commit hooks (they are installed in their own environment and thus do not conflict w/ the local installations you may have).

##### Running pre-commit hooks manually

Pre-commit hooks are run on each commit automatically. Still, you can run them manually if you need to.

Run all hooks:
```
pre-commit run --all-files
```

Run a certain hook:
```
pre-commit run <hook_id> --all-files
```
where `<hook_id>` is a hook ID from `./.pre-commit-config.yaml`.

You can also `run` hook(s) on specific file(s) w/ `--files <list of files>` argument. See [all possible arguments](https://pre-commit.com/#pre-commit-run) in `pre-commit`'s documentation.

## Production
Monocle is available internally to Sanger at the following addresses:
- `prod`: [http://monocle.pam.sanger.ac.uk/](http://monocle.pam.sanger.ac.uk/)
- `dev`: [http://monocle.dev.pam.sanger.ac.uk/](http://monocle.dev.pam.sanger.ac.uk/) (likely to be broken)

This project is early in development, so subject to change, but the current release and deploy process is described below.

### Making a release
Currently, to make a release, make sure you are on the `master` branch with nothing to commit, then run:
```
./release.sh <version>
```
Note: `<version>` should conform to [semver](https://semver.org/).

### Deployment

#### Secrets

The procedures for storing and deploying secrets and other configurartion
specific to the individual deployments of Monocle are privately documented.  The
end product of these proecures is to provide the following files:
- `mlwh-api.yml` for the Sanger MLWH API
- `my.cnf` for database connection
- `openldap-env.yaml` for OpenLDAP


#### LDAP data backup

Before proceeding with the deployment, make sure you have backed up the groups and users from the
LDAP service as an LDIF file.  Log in as `admin` at `/ldap-admin'
(the password is in your `openldap-env.yaml` file) and use the "Export" function; be certain to
export the entire subtree.

The export will contain two entries that you should delete (probably the first two entries):
the base DN entry and the "LDAP read only user".   These should be removed because these two
entries are automatically created when the service is started, from your config file.  If you
were to change your config then the base DN and readonly user account will change;  importing
something save in an LDIF file from an earlier release may overwrite these entries in LDAP with
outdated entries.  This is really quite high up the list of things you don't want to do.

#### Deploying a release

Wait until the CI pipeline has completed.

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
- An additional `-c <path to mysql connection file>` argument must be passed to the deploy.sh script. The connection file must contain the connection details for the database instance to be updated.

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


### Recovering from access control problems following deployment

If you have made changes to LDAP configuration that are incompatible with the
data stored by your LDAP service, this could result in being denied access. This
is most likely to occur if you have updated `openldap-env.yaml`, but there is
configuration related to OpenLDAP in `docker-compose.yml` and
`nginx.proxy.conf`.

Before deployment, you will have exported group and user accounts from LDAP as
an LDIF file (see "LDAP data backup" above).   (If not, roll back to the previous
release and so so.)

Stop the service, then back up and delete the subdirectories `openldap-data` and
`phpldapadmin-data` on the machine you are running the service on.  Then restart
the service. This will recreate these directories, and configure the LDAP
service with the correct base DN and readonly user account from your config
files.   There will be no groups or user accounts in the LDAP service, so log in
as `admin` at `/ldap-admin' (the password is in your `openldap-env.yaml` file)
and import the LDIF file you saved earlier.


## Data

In production, the real data files are loaded from an S3 bucket, which is synced from farm5.
If you have Sanger credentials, see the companion gitlab repo
[monocle-farm5](https://gitlab.internal.sanger.ac.uk/sanger-pathogens/monocle-farm5).

For development and testing, lightweight mock data for a single lane is used. See
the `mock-data` directory within the repo.
