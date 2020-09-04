import json
import random
from django.core.management import BaseCommand

from juno.api.models import User, Institution, Affiliation, Sample


class Command(BaseCommand):
    help = "Load sample data for end-to-end tests [TEST ONLY]"

    PROFILES = ["empty", "small", "large"]

    def add_arguments(self, parser):
        parser.add_argument("profile", choices=self.PROFILES)

    def handle(self, *args, **options):
        # validate profile
        profile = options["profile"]
        if profile not in self.PROFILES:
            raise ValueError(
                "Invalid profile argument. Supported: {}".format(self.PROFILES)
            )

        # switch profile and set db content
        if profile == "empty":
            self.empty()
        elif profile == "small":
            self.small()
        elif profile == "large":
            self.large()

        # return json-serialised db content for test assertions
        data = {
            "user": list(User.objects.values()),
            "institution": list(Institution.objects.values()),
            "affiliation": list(Affiliation.objects.values()),
            "sample": list(Sample.objects.values()),
        }
        return json.dumps(data)

    def clear(self):
        User.objects.all().delete()
        Institution.objects.all().delete()
        Affiliation.objects.all().delete()
        Sample.objects.all().delete()

    def set_passwords_as_email_prefix(self):
        # fix the passwords of users to be email prefix
        # (ie. before the @ symbol)
        for user in User.objects.all():
            user.set_password(user.email.split("@")[0])
            user.save()

    def empty(self):
        self.clear()

        # users (need to be able to log in)
        User.objects.create(
            email="admin@sanger.ac.uk", first_name="Alice", last_name="Jones"
        )
        self.set_passwords_as_email_prefix()

    def small(self):
        self.clear()

        # users
        admin = User.objects.create(
            email="admin@sanger.ac.uk", first_name="Alice", last_name="Jones"
        )
        collaborator = User.objects.create(
            email="collaborator@nrl.israel",
            first_name="Bob",
            last_name="Smith",
        )
        collaborator_multiple = User.objects.create(
            email="collaborator@multiple.com",
            first_name="Howard",
            last_name="Jenkins",
        )
        self.set_passwords_as_email_prefix()

        # institutions
        sanger = Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )
        nrl = Institution.objects.create(
            name="National Reference Laboratories",
            country="Israel",
            latitude=32.083333,
            longitude=34.8,
        )
        cuhk = Institution.objects.create(
            name="The Chinese University of Hong Kong",
            country="China",
            latitude=22.419722,
            longitude=114.206792,
        )

        # affiliations
        Affiliation.objects.create(user=admin, institution=sanger)
        Affiliation.objects.create(
            user=collaborator, institution=nrl,
        )
        Affiliation.objects.create(
            user=collaborator_multiple, institution=nrl,
        )
        Affiliation.objects.create(
            user=collaborator_multiple, institution=cuhk,
        )

        # samples
        Sample.objects.create(
            lane_id="31663_7#113",
            sample_id="5903STDY8059170",
            public_name="CUHK_GBS177WT_16",
            serotype="Ia",
            host_status="skin and soft-tissue infection",
            submitting_institution=nrl,
        )
        Sample.objects.create(
            lane_id="31663_7#115",
            sample_id="5903STDY8059071",
            public_name="NA",
            serotype="Ib",
            host_status="meningitis",
            submitting_institution=nrl,
        )
        Sample.objects.create(
            lane_id="32820_2#367",
            sample_id="5903STDY8113194",
            public_name="JN_IL_ST31578",
            serotype="VI",
            host_status="pneumonia",
            submitting_institution=cuhk,
        )
        Sample.objects.create(
            lane_id="32820_2#368",
            sample_id="5903STDY8113195",
            public_name="JN_IL_ST31579",
            serotype="V",
            host_status="pneumonia",
            submitting_institution=sanger,
        )

    def large(self):
        self.clear()

        # users
        admin = User.objects.create(
            email="admin@sanger.ac.uk", first_name="Alice", last_name="Jones"
        )
        collaborator = User.objects.create(
            email="collaborator@nrl.israel",
            first_name="Bob",
            last_name="Smith",
        )
        collaborator_multiple = User.objects.create(
            email="collaborator@multiple.com",
            first_name="Howard",
            last_name="Jenkins",
        )
        self.set_passwords_as_email_prefix()

        # institutions
        sanger = Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )
        nrl = Institution.objects.create(
            name="National Reference Laboratories",
            country="Israel",
            latitude=32.083333,
            longitude=34.8,
        )
        cuhk = Institution.objects.create(
            name="The Chinese University of Hong Kong",
            country="China",
            latitude=22.419722,
            longitude=114.206792,
        )

        # affiliations
        Affiliation.objects.create(user=admin, institution=sanger)
        Affiliation.objects.create(
            user=collaborator, institution=nrl,
        )
        Affiliation.objects.create(
            user=collaborator_multiple, institution=nrl,
        )
        Affiliation.objects.create(
            user=collaborator_multiple, institution=cuhk,
        )

        # samples
        for i in range(40):
            lane_id = "31663_7#{}".format(113 + i)
            sample_id = "5903STDY{}".format(8059170 + i)
            public_name = "CUHK_GBS177WT_{}".format(26 + i)
            serotype = random.choice(
                ["Ia", "Ib", "II", "III", "VII", "unknown"]
            )
            host_status = random.choice(
                ["carriage", "bacteraemia", "urinary tract infection"]
            )
            submitting_institution = random.choice([sanger, nrl, cuhk])

            Sample.objects.create(
                lane_id=lane_id,
                sample_id=sample_id,
                public_name=public_name,
                serotype=serotype,
                host_status=host_status,
                submitting_institution=submitting_institution,
            )
