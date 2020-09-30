import time
from django.db import connection
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


# see https://stackoverflow.com/questions/32098797/how-can-i-check-database-connection-to-mysql-in-django


class Command(BaseCommand):
    """Django command that waits for database to be available"""

    def handle(self, *args, **options):
        """Handle the command"""
        self.stdout.write("Waiting for database...")
        db_conn = None
        attempts = 0
        while not db_conn and attempts < 10:
            attempts += 1
            try:
                connection.ensure_connection()
                db_conn = True
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))
