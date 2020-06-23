from django.core.management import BaseCommand, call_command

from juno.api.models import User, Institution, Affiliation, Sample

# TODO: work out the best way to manage e2e fixtures
#       (more flexibility in cypress is probably good)


class Command(BaseCommand):
    help = "Load sample data for end-to-end tests [TEST ONLY]"

    PROFILES = ["empty", "small"]

    def add_arguments(self, parser):
        parser.add_argument("profile", choices=self.PROFILES)

    def handle(self, *args, **options):
        profile = options["profile"]
        if profile not in self.PROFILES:
            raise ValueError(
                "Invalid profile argument. Supported: {}".format(self.PROFILES)
            )

        # switch profile
        if profile == "empty":
            self.clear_all()
        elif profile == "small":
            self.clear_all()
            self.add_users_small()
            self.add_institutions_small()
            self.add_affiliations_small()
            self.add_samples_small()
            self.set_default_passwords()

    def clear_all(self):
        User.objects.all().delete()
        Institution.objects.all().delete()
        Affiliation.objects.all().delete()
        Sample.objects.all().delete()

    def add_users_small(self):
        User.objects.create(
            email="admin@sanger.ac.uk", first_name="Alice", last_name="Jones"
        )
        User.objects.create(
            email="collaborator@nrl.israel",
            first_name="Bob",
            last_name="Smith",
        )

    def add_institutions_small(self):
        Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )
        Institution.objects.create(
            name="National Reference Laboratories",
            country="Israel",
            latitude=32.083333,
            longitude=34.8,
        )

    def add_affiliations_small(self):
        Affiliation.objects.create(
            user="admin@sanger.ac.uk", institution="Wellcome Sanger Institute"
        )
        Affiliation.objects.create(
            user="collaborator@nrl.israel",
            institution="National Reference Laboratories",
        )

    def add_samples_small(self):
        # TODO: Use ORM instead of fixtures
        call_command("loaddata", "samples")

    def set_default_passwords(self):
        # fix the passwords of fixtures to be email prefix
        for user in User.objects.all():
            user.set_password(user.email.split("@")[0])
            user.save()
