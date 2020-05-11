from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from juno.database import db
from juno.graphql.models import UserModel

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