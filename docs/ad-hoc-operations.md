# Ad Hoc Operations

Below is a brief overview of how to do various operations that are semi-independent of software releases, such as:
- database migrations
- account management (adding/removing users, institutions)

The dev/prod MySQL databases live on IGM managed hosts, with connection details and credentials currently stored in the `my.cnf` file on the OpenStack VM and volume mounted into the `api` container. In what follows, `ssh`-ing into the OpenStack VM and running a Django management command via the `api` container requires no setup (alternatively, you could copy the `my.cnf` locally, then run eg. `python manage.py <command> --settings 'juno.settings.prod'` from you laptop).

## Database Migrations
Databases are manually created with MySQL client. Schema migrations, including initial creation of tables, are managed by [Django's migration system](https://docs.djangoproject.com/en/3.1/topics/migrations/), based on the ORM models in `models.py`.

To run migrations, `ssh` into the dev/prod OpenStack VM and run:
```
docker-compose exec api python manage.py migrate
```

## Account Management
Users and institutions could be added/removed using SQL directly, but going through the Django ORM should provide some additional checks. Future work should identify and formalise the common operations, such that they can be done through the UI or, at least, without needing to `ssh` into the OpenStack VM directly. At present, using Django's `manage.py` commands is fairly straightforward.

### Shell
To make small changes to a small number of users/institutions, `ssh` into the dev/prod OpenStack VM and run:
```
docker-compose exec api python manage.py shell
```

You can now use the Django ORM models/querysets to create/edit/remove entries from the database:
```
from juno.api.models import User, Institution, Affiliation

u = User(first_name="Lex", last_name="Luther", email="megalo@maniacs.com")
u.set_password("something-secret")
u.save()
```

### Loaddata
To make bulk additions to users/institutions, `ssh` into the dev/prod OpenStack VM and run:
```
docker-compose exec api python manage.py loaddata <json-data-file>
```

The format of the `<json-data-file>` is described [here](https://docs.djangoproject.com/en/3.1/ref/django-admin/#loaddata). There is also a similar `python manage.py dumpdata` command that can be used to produce a backup.
