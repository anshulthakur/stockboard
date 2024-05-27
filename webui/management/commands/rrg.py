from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument('-d', '--daily', action='store_true', default = False, help="Compute RRG on daily TF")
        parser.add_argument('-w', '--weekly', action='store_true', default = True, help="Compute RRG on weekly TF")
        parser.add_argument('-m', '--monthly', action='store_true', default = False, help="Compute RRG on monthly TF")
        parser.add_argument('-o', '--online', action='store_true', default = False, help="Fetch data from TradingView (Online)")
        parser.add_argument('-f', '--for', dest='date', help="Compute RRG for date")
        parser.add_argument('-n', '--nodownload', dest='download', action="store_false", default=True, help="Do not attempt download of indices")
        parser.add_argument('-r', '--refresh', dest='refresh', action="store_true", default=False, help="Refresh index constituents files")

    def handle(self, *args, **options):
        pass   