import os
import click
from flask.cli import with_appcontext
from flask_fixtures import load_fixtures_from_file

from .database import db
from .graphql.models import UserModel

@click.command()
@with_appcontext
def load_fixtures():
    """Load mock fixtures for development."""
    
    print('Loading fixtures...')
    current_dir = os.path.abspath(os.path.dirname(__file__))  # This directory
    fixtures_dir = os.path.join(current_dir, 'fixtures')
    load_fixtures_from_file(db, 'dev.json', [fixtures_dir])
    print('Done.')
