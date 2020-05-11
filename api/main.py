from flask import Flask
from flask.cli import AppGroup
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
import click

# ------------------  app setup ------------------

# init app
app = Flask(__name__)

# config
app.config.from_envvar('API_CONFIG_FILE')

# init db
db = SQLAlchemy(app)

# ------------------  custom cli methods ------------------

juno_cli = AppGroup('juno')

@juno_cli.command('load')
def load():
    # create tables
    print('Creating tables...')
    db.create_all()
    print('Done.')

    # create some mock data
    print('Creating sample users...')
    gp16 = UserModel(first_name="Gareth", last_name="Peat", email="gp16@sanger.ac.uk")
    cp15 = UserModel(first_name="Christoph", last_name="Puethe", email="cp15@sanger.ac.uk")
    os7 = UserModel(first_name="Oli", last_name="Seret", email="os7@sanger.ac.uk")
    db.session.add(gp16)
    db.session.add(cp15)
    db.session.add(os7)
    db.session.commit()
    print('Done.')

    print(UserModel.query.all())

app.cli.add_command(juno_cli)

# ------------------  database models ------------------

class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email


# ------------------ GraphQL schema ------------------

class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel


class Query(graphene.ObjectType):
    users = graphene.List(User)

    def resolve_users(self, info, **kwargs):
        return UserModel.query.all()


class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    user = graphene.Field(lambda: User)

    def mutate(self, info, email, first_name, last_name):
        user = UserModel.query.filter_by(email=email).first()
        if user is not None:
            print("Already exists!")
        user = UserModel(email=email, first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()
        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)

app.add_url_rule('/', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True
))
