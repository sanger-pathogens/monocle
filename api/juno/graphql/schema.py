from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy.types import ORMField

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
        exclude_fields = (
            'submitting_institution',
            'submitting_institution_object'
        )

    submitting_institution = ORMField(
        model_attr='submitting_institution_object',
        required=True
    )


class Query(graphene.ObjectType):
    users = graphene.List(User) # TODO: eventually remove users query for privacy
    institutions = graphene.List(Institution)
    samples = graphene.List(Sample)

    def resolve_users(self, info, **kwargs):
        return UserModel.query.all()
    
    def resolve_institutions(self, info, **kwargs):
        return InstitutionModel.query.all()

    def resolve_samples(self, info, **kwargs):
        return SampleModel.query.all()


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