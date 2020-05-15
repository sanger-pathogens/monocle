import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from flask_graphql_auth import (
    AuthInfoField,
    create_access_token,
    create_refresh_token,
    query_jwt_required,
)

from juno.database import db
from juno.graphql.models import UserModel, InstitutionModel, SampleModel


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel

    # affiliated_institutions = graphene.List(Institution)

    # def resolve_affiliated_institutions(self, info, **kwargs):
    #     # TODO: work this out
    #     pass


class Institution(SQLAlchemyObjectType):
    class Meta:
        model = InstitutionModel


class Sample(SQLAlchemyObjectType):
    class Meta:
        model = SampleModel


class MessageField(graphene.ObjectType):
    message = graphene.String()


class ProtectedUnion(graphene.Union):
    class Meta:
        types = (MessageField, AuthInfoField)

    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)


class Query(graphene.ObjectType):
    users = graphene.List(User)  # TODO: eventually remove users query for privacy
    institutions = graphene.List(Institution)
    samples = graphene.List(Sample)
    protected = graphene.Field(type=ProtectedUnion, token=graphene.String())

    def resolve_users(self, info, **kwargs):
        return UserModel.query.all()

    def resolve_institutions(self, info, **kwargs):
        return InstitutionModel.query.all()

    def resolve_samples(self, info, **kwargs):
        return SampleModel.query.all()

    @query_jwt_required
    def resolve_protected(self, info):
        return MessageField(message="This is private!")


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


class LoginMutation(graphene.Mutation):
    class Arguments(object):
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    access_token = graphene.String()
    refresh_token = graphene.String()

    @classmethod
    def mutate(cls, _, info, email, password):
        # TODO: check password

        user = UserModel.query.filter_by(email=email).first()
        user_claims = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "affiliated_institutions": [
                institution.name for institution in user.affiliated_institutions
            ],
        }

        # TODO: Remove refresh_token from graphql and set cookie
        #       in response header with HttpOnly=True on cookie
        return LoginMutation(
            access_token=create_access_token(email, user_claims=user_claims),
            refresh_token=create_refresh_token(email, user_claims=user_claims),
        )


# class RefreshMutation(graphene.Mutation):
#     class Arguments(object):
#         token = graphene.String()

#     new_token = graphene.String()

#     @classmethod
#     @mutation_jwt_refresh_token_required
#     def mutate(self, _, info):
#         current_user = get_jwt_identity()
#         return RefreshMutation(
#             new_token=create_access_token(
#                 identity=current_user, user_claims=user_claims
#             )
#         )


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login = LoginMutation.Field()
    # refresh = RefreshMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
