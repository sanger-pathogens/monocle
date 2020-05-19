from django.core.management import BaseCommand, call_command

from juno.api.models import User


class Command(BaseCommand):
    help = "Load sample data for development [DEV ONLY]"

    def handle(self, *args, **options):
        # equivalent to running eg. `python manage.py loaddata users.json`
        call_command("loaddata", "users")
        call_command("loaddata", "institutions")
        call_command("loaddata", "affiliations")
        call_command("loaddata", "samples")

        # fix the passwords of fixtures to be email prefix
        for user in User.objects.all():
            user.set_password(user.email.split("@")[0])
            user.save()
