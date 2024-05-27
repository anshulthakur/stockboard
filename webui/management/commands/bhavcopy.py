from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument('-m', '--market', help="Market (NSE/BSE/MCX/...)")
        parser.add_argument('-d', '--date', help="Date")
        parser.add_argument('-b', '--bulk', help="Get bulk data for stock(s)", action="store_true", default=False)

    def handle(self, *args, **options):
        pass   