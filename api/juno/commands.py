import click
from flask.cli import with_appcontext

from .database import db
from .graphql.models import UserModel

@click.command()
@with_appcontext
def load_fixtures():
    """Load mock fixtures for development."""

    print('Creating sample users...')
    gp16 = UserModel(first_name="Gareth", last_name="Peat", email="gp16@sanger.ac.uk")
    cp15 = UserModel(first_name="Christoph", last_name="Puethe", email="cp15@sanger.ac.uk")
    os7 = UserModel(first_name="Oli", last_name="Seret", email="os7@sanger.ac.uk")
    db.session.add(gp16)
    db.session.add(cp15)
    db.session.add(os7)
    db.session.commit()
    print('Done.')
