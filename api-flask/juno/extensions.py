from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_graphql_auth import GraphQLAuth

bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
auth = GraphQLAuth
