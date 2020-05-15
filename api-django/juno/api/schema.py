import graphene
from graphene_django.types import DjangoObjectType
from graphql_jwt import ObtainJSONWebToken, Verify, Refresh
from graphql_jwt.decorators import login_required


from juno.api import models


class Institution(DjangoObjectType):
    class Meta:
        model = models.Institution


class User(DjangoObjectType):
    class Meta:
        model = models.User


class Sample(DjangoObjectType):
    class Meta:
        model = models.Sample


class Mutation(object):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()
    refresh_token = Refresh.Field()


class Query(object):
    me = graphene.Field(User)
    samples = graphene.List(Sample)
    institutions = graphene.List(Institution)

    @login_required
    def resolve_me(self, info, **kwargs):
        return info.context.user

    def resolve_samples(self, info, **kwargs):
        # TODO: add pagination
        # TODO: add filtering/sorting for columns
        return models.Sample.objects.all()

    def resolve_institutions(self, info, **kwargs):
        # TODO: remove this (just for debug)
        return models.Institution.objects.all()
