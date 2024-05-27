import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from django.conf import settings
from django.apps import apps

import settings as setting
from libinit import is_initialized, initialize

conf = {}
for mod in dir(setting):
    if mod.isupper():
        conf[mod] = getattr(setting, mod)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIRS = {
    'reports': os.path.join(BASE_DIR, "reports/"), 
    'cache'  : os.path.join(BASE_DIR, "runtime/cache"),
    'intraday': os.path.join(BASE_DIR, "intraday/"),
    'rrg'   :   os.path.join(BASE_DIR, "runtime/rrg"),
}

RRG_PROGRESS_FILE = os.path.join(PROJECT_DIRS.get('rrg'), ".progress.json")


if not is_initialized():
    print("Initializing")
    settings.configure(**conf)
    apps.populate(settings.INSTALLED_APPS)
    initialize()