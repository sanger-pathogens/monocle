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

    def resolve_samples(self, info, **kwargs):
        return models.Sample.objects.all()
