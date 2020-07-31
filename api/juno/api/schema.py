from django.db import DatabaseError, transaction
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
        commit = graphene.NonNull(graphene.Boolean)

    committed = graphene.NonNull(graphene.Boolean)
    removed = graphene.NonNull(graphene.List(Sample))
    added = graphene.NonNull(graphene.List(Sample))
    changed = graphene.NonNull(graphene.List(Sample))

    @classmethod
    def mutate(cls, root, info, samples, commit, *args, **kwargs):
        # TODO: consider that lane_id is not really metadata
        # (metadata should be indexed by public name, since
        # lane_id is sequencing related and may not be known)
        committed = False
        try:
            with transaction.atomic():
                # retrieve samples from db
                samples_in_db = models.Sample.objects.all()

                # validate (with renamed field fk field)
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

                # diff
                # (return db versions, since client has prepared,
                # so it can then potentially show diff)
                sample_ids_in_db = set(
                    sample.lane_id for sample in samples_in_db
                )
                sample_ids_in_prepared = set(
                    sample.lane_id for sample in samples_prepared
                )
                samples_added = [
                    sample
                    for sample in samples_prepared
                    if sample.lane_id not in sample_ids_in_db
                ]
                samples_removed = [
                    sample
                    for sample in samples_in_db
                    if sample.lane_id not in sample_ids_in_prepared
                ]
                samples_changed = [
                    sample
                    for sample in samples_in_db
                    if sample.lane_id in sample_ids_in_prepared
                ]

                # only make the change if requested
                # (so diff can be computed without commit)
                if commit:
                    # clear samples table in db
                    samples_in_db.delete()

                    # insert new entries
                    models.Sample.objects.bulk_create(samples_prepared)

                    committed = True
        # except DatabaseError:
        #     return UpdateSamplesMutation(ok=False)
        except Exception:
            return UpdateSamplesMutation(
                committed=committed, removed=[], added=[], changed=[]
            )

        return UpdateSamplesMutation(
            committed=committed,
            removed=samples_removed,
            added=samples_added,
            changed=samples_changed,
        )


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
