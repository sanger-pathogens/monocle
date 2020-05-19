from django.core.management import BaseCommand
from graphql.utils import schema_printer

from juno.schema import schema


class Command(BaseCommand):
    help = "Generate schema.graphql"

    def handle(self, *args, **options):
        with open("schema.graphql", "w") as f:
            schema_str = schema_printer.print_schema(schema)
            f.write(schema_str)
