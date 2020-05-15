import graphene

from graphene_django.types import DjangoObjectType

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


class Query(object):
    samples = graphene.List(Sample)
    institutions = graphene.List(Institution)

    def resolve_samples(self, info, **kwargs):
        # TODO: add pagination
        # TODO: add filtering/sorting for columns
        return models.Sample.objects.all()

    def resolve_institutions(self, info, **kwargs):
        # TODO: remove this (just for debug)
        return models.Institution.objects.all()
