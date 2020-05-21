# GraphQL API (Django)

This is experimental.

## Stack background
If you've not used Django and/or GraphQL before, it would be worth running through the following tutorials and documentation.

* [Django](https://docs.djangoproject.com/en/3.0/intro/tutorial01/)
* [Graphene](https://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/)
* [JWT](https://jwt.io/introduction/)
* [JWT with Django and GraphQL](https://django-graphql-jwt.domake.io/en/latest/quickstart.html)

## Development

This API was bootstrapped with [Django](https://www.djangoproject.com/). See their documentation for options.

### Quickstart
Ensure you have `python3` installed.

Load the environment defined by the `Pipfile` and `Pipfile.lock` (note: you should not need to update these files manually):
```
pipenv install
pipenv shell
```

Create a `sqlite3` database and load some sample data:
```
python manage.py migrate
python manage.py loaddev
python manage.py collectstatic
```

Run the development server:
```
python manage.py runserver
```

You should be able to view the `graphiql` interactive schema at `localhost:5000`.

### Testing
You can run the tests with:
```
python manage.py test
```

### Migrations
You can create any necessary migrations with:
```
python manage.py makemigrations api
```

Note: The above takes account of the existing `migrations` in the `juno/api/migrations` directory. Early on, while the database can be easily destroyed, it may easier to remove the directory entirely before running, to *squash* them.

To apply the migrations, run:
```
python manage.py migrate
```

### Schemas

#### Database
You can regenerate the database schema diagram with:
```
python manage.py graph_models -a -g -X Permission,ContentType,Group -o schema-db.png
```

Note: You might need to `brew install graphviz`. Also, `Permission,ContentType,Group` are Django built-in classes, excluded for clarity.

#### GraphQL API
You can regenerate the GraphQL API schema file with:
```
python manage.py generateschemagraphql
```
