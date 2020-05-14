import os
import click
from flask.cli import with_appcontext
from flask_fixtures import load_fixtures_from_file

from .database import db
from .graphql.models import UserModel

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
FIXTURES_DIR = os.path.join(HERE, 'fixtures')
TESTS_DIR = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
def test():
    """Run the tests."""
    import pytest
    rv = pytest.main([TESTS_DIR, '--verbose'])
    exit(rv)


@click.command()
@with_appcontext
def load_fixtures():
    """Load mock fixtures for development."""
    
    print('Loading fixtures...')
    load_fixtures_from_file(db, 'dev.json', [FIXTURES_DIR])
    print('Done.')
