"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    # TODO: change SECRET_KEY for production
    SECRET_KEY = os.environ.get("JUNO_SECRET_KEY", "secret-key")
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # temporary
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        PROJECT_ROOT, "database.sqlite"
    )
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    JWT_SECRET_KEY = "something"  # TODO: change
    REFRESH_EXP_LENGTH = 30
    ACCESS_EXP_LENGTH = 10


class ProdConfig(Config):
    """Production configuration."""

    ENV = "prod"
    DEBUG = False
    # TODO: Set up MySQL for SQLAlchemy


class DevConfig(Config):
    """Development configuration."""

    ENV = "dev"
    DEBUG = True
    CORS_ORIGIN_WHITELIST = "http://localhost:3000"


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    BCRYPT_LOG_ROUNDS = 4
