# GraphQL API (Django)

This is experimental.

## Stack background
If you've not used Django and/or GraphQL before, it would be worth running through the following tutorials and documentation.

* [Django](https://docs.djangoproject.com/en/3.0/intro/tutorial01/)
* [Graphene](https://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/)
* [JWT](https://jwt.io/introduction/)
* [JWT with Django and GraphQL](https://django-graphql-jwt.domake.io/en/latest/quickstart.html)

## Development

### Quickstart
Load the environment defined by the `Pipfile` and `Pipfile.lock`:
```
pipenv install
pipenv shell
```

Create a `sqlite3` database and load some sample data:
```
python manage.py migrate
python manage.py loaddev
```

Run the development server:
```
python manage.py runserver
```

You should be able to view the `graphiql` interactive schema at `localhost:5000`.

### Migrations

### Schema diagram
You can regenerate the schema diagram with:
```
python manage.py graph_models -a -g -X Permission,ContentType,Group -o schema-db.png
```

Note: You might need to `brew install graphviz`. Also, `Permission,ContentType,Group` are Django built-in classes, excluded for clarity.