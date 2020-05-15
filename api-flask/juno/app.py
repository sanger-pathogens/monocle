from flask import Flask

from juno.extensions import bcrypt, db, migrate, cors, auth
from juno import commands, graphql
from juno.settings import ProdConfig


def create_app(config_object=ProdConfig):
    """Application factory"""
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    auth(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    origins = app.config.get("CORS_ORIGIN_WHITELIST", "*")
    cors.init_app(
        graphql.views.blueprint, origins=origins, supports_credentials=True
    )

    app.register_blueprint(graphql.views.blueprint)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.load_fixtures)
