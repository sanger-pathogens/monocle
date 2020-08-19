from django.db import transaction
from graphene import (
    ObjectType,
    NonNull,
    Mutation,
    List,
    Boolean,
    String,
)
from graphql_jwt import (
    ObtainJSONWebToken,
    Verify,
    Refresh,
)
from graphql_jwt.decorators import login_required
from graphene_django_extras import (
    DjangoObjectType,
    DjangoListObjectType,
    DjangoInputObjectType,
    DjangoListObjectField,
    LimitOffsetGraphqlPagination,
)

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


class SampleList(DjangoListObjectType):
    class Meta:
        description = " Type definition for user list "
        model = models.Sample
        pagination = LimitOffsetGraphqlPagination(
            default_limit=10, ordering="lane_id"
        )


# see https://github.com/eamigo86/graphene-django-extras/issues/41
class SampleListField(DjangoListObjectField):
    @login_required
    def list_resolver(
        self, manager, filterset_class, filtering_args, root, info, **kwargs
    ):
        return super(SampleListField, self).list_resolver(
            manager, filterset_class, filtering_args, root, info, **kwargs
        )


class SampleInput(DjangoInputObjectType):
    class Meta:
        model = models.Sample


class SamplesDiff(ObjectType):
    removed = NonNull(List(NonNull(Sample)))
    added = NonNull(List(NonNull(Sample)))
    changed = NonNull(List(NonNull(Sample)))
    same = NonNull(List(NonNull(Sample)))
    missing_institutions = NonNull(List(NonNull(String)))


def deep_compare(sample1, sample2):
    # helper to compare each field for a submitted sample
    # against the db version
    return all(
        sample1.__dict__[field] == sample2.__dict__[field]
        for field in sample1.__dict__
        if field != "_state"
    )


def diff_samples(samples_db, samples_to_compare):
    # build look up tables
    samples_db_lut = {sample.lane_id: sample for sample in samples_db}
    samples_to_compare_lut = {
        sample.lane_id: sample for sample in samples_to_compare
    }

    # get id sets
    samples_db_ids = set(samples_db_lut.keys())
    samples_to_compare_ids = set(samples_to_compare_lut.keys())

    # diff on id sets
    sample_ids_common = samples_to_compare_ids & samples_db_ids
    sample_ids_added = samples_to_compare_ids - samples_db_ids
    sample_ids_removed = samples_db_ids - samples_to_compare_ids
    sample_ids_same = set(
        sample_id
        for sample_id in sample_ids_common
        if deep_compare(
            samples_to_compare_lut[sample_id], samples_db_lut[sample_id]
        )
    )
    sample_ids_changed = sample_ids_common - sample_ids_same

    # diff on full samples
    added = [
        samples_to_compare_lut[sample_id] for sample_id in sample_ids_added
    ]
    removed = [samples_db_lut[sample_id] for sample_id in sample_ids_removed]
    changed = [samples_db_lut[sample_id] for sample_id in sample_ids_changed]
    same = [samples_db_lut[sample_id] for sample_id in sample_ids_same]

    # missing institutions?
    institutions_db = set(
        institution.name for institution in models.Institution.objects.all()
    )
    institutions_to_compare = set(
        sample.submitting_institution_id for sample in samples_to_compare
    )
    missing_institutions = [
        institution
        for institution in institutions_to_compare
        if institution not in institutions_db
    ]

    # return diff
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "same": same,
        "missing_institutions": missing_institutions,
    }


def deserialise_samples(samples):
    # handle foreign key
    return [
        models.Sample(
            submitting_institution_id=sample.submitting_institution,
            **{
                key: value
                for key, value in sample.items()
                if key != "submitting_institution"
            },
        )
        for sample in samples
    ]


class UpdateSamplesMutation(Mutation):
    class Arguments:
        samples = NonNull(List(NonNull(SampleInput)))

    committed = NonNull(Boolean)
    diff = NonNull(SamplesDiff)

    @classmethod
    def mutate(cls, root, info, samples, *args, **kwargs):
        # TODO: consider that lane_id is not really metadata
        # (metadata should be indexed by public name, since
        # lane_id is sequencing related and may not be known)
        committed = False
        with transaction.atomic():
            # retrieve samples from db
            samples_db = models.Sample.objects.all()

            # validate (with renamed fk field)
            samples_to_compare = deserialise_samples(samples)

            # compute diff
            diff = diff_samples(samples_db, samples_to_compare)

            # only make there are no missing institutions
            if len(diff["missing_institutions"]) == 0:
                # clear samples table in db
                samples_db.delete()

                # insert new entries
                models.Sample.objects.bulk_create(samples_to_compare)

                committed = True

        return UpdateSamplesMutation(committed=committed, diff=diff)


class Mutation(object):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()
    refresh_token = Refresh.Field()
    delete_token_cookie = DeleteTokens.Field()

    update_samples = UpdateSamplesMutation.Field()


class Query(object):
    me = NonNull(User)
    samples = NonNull(List(NonNull(Sample)))
    samples_list = SampleListField(SampleList)
    institutions = NonNull(List(NonNull(Institution)))
    compare_samples = NonNull(
        SamplesDiff, samples=NonNull(List(NonNull(SampleInput)))
    )

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

    @login_required
    def resolve_compare_samples(self, info, samples):
        # retrieve samples from db
        samples_db = models.Sample.objects.all()

        # validate (with renamed fk field)
        samples_to_compare = deserialise_samples(samples)

        # compute diff
        diff = diff_samples(samples_db, samples_to_compare)

        return diff
