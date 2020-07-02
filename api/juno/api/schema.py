import graphene
from graphene_django.types import DjangoObjectType
from graphql_jwt import (
    ObtainJSONWebToken,
    Verify,
    Refresh,
    DeleteJSONWebTokenCookie,
)
from graphql_jwt.decorators import login_required


from juno.api import models


class Institution(DjangoObjectType):
    class Meta:
        model = models.Institution


class User(DjangoObjectType):
    class Meta:
        model = models.User
        exclude_fields = (
            "password",
            "last_login",
        )


class Sample(DjangoObjectType):
    class Meta:
        model = models.Sample


class Mutation(object):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()
    refresh_token = Refresh.Field()
    delete_token_cookie = DeleteJSONWebTokenCookie.Field()


class Query(object):
    me = graphene.Field(User)
    samples = graphene.List(Sample)
    institutions = graphene.List(Institution)

    @login_required
    def resolve_me(self, info, **kwargs):
        return info.context.user

    @login_required
    def resolve_samples(self, info, **kwargs):
        # TODO: add pagination
        # TODO: add filtering/sorting for columns

        # get user's affiliations
        affiliations = info.context.user.affiliations

        # sanger user's can see everything
        if (
            affiliations.filter(
                name__exact="Wellcome Sanger Institute"
            ).count()
            > 0
        ):
            return models.Sample.objects.all()
        else:
            return models.Sample.objects.filter(
                submitting_institution__affiliated_members__in=[
                    info.context.user
                ]
            ).all()

    @login_required
    def resolve_institutions(self, info, **kwargs):
        # get user's affiliations
        affiliations = info.context.user.affiliations

        # sanger user's can see everything
        if (
            affiliations.filter(
                name__exact="Wellcome Sanger Institute"
            ).count()
            > 0
        ):
            return models.Institution.objects.all()
        else:
            return affiliations.all()
