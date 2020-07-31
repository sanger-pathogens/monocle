import graphene
from graphene_django.types import DjangoObjectType
from graphql_jwt import (
    ObtainJSONWebToken,
    Verify,
    Refresh,
)
from graphql_jwt.decorators import login_required
from graphene_django_extras import DjangoInputObjectType

from juno.api.delete_tokens_mutation import DeleteTokens
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


class SampleInput(DjangoInputObjectType):
    class Meta:
        model = models.Sample


class UpdateSamplesMutation(graphene.Mutation):
    class Arguments:
        samples = graphene.NonNull(graphene.List(SampleInput))

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, samples, *args, **kwargs):
        try:
            with transaction.atomic():
                # retrieve samples from db
                samples_in_db = models.Sample.objects.all()

                # diff and validate (with renamed field fk field)
                samples_prepared = [
                    models.Sample(
                        **{
                            key: value
                            for key, value in sample.items()
                            if key != "submitting_institution"
                        },
                        **{
                            "submitting_institution_id": sample.submitting_institution
                        }
                    )
                    for sample in samples
                ]

                # clear samples table in db
                samples_in_db.delete()

                # insert new entries
                models.Sample.objects.bulk_create(samples_prepared)
        # except DatabaseError:
        #     return UpdateSamplesMutation(ok=False)
        except Exception:
            return UpdateSamplesMutation(ok=False)

        return UpdateSamplesMutation(ok=True)


class Mutation(object):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()
    refresh_token = Refresh.Field()
    delete_token_cookie = DeleteTokens.Field()

    update_samples = UpdateSamplesMutation.Field()


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
