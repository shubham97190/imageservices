import glob, os
from datetime import datetime, timedelta
from django.conf import settings

def removeOldImages():
    print('gfzsgisa')
    removing_date = (datetime.now()-timedelta(days=31)).strftime('%d-%m-%Y')
    for filenames in glob.glob(settings.STATICFILES_DIRS[1]+"/*.png"):
        created = os.path.getctime(filenames)
        if datetime.fromtimestamp(created).strftime('%d-%m-%Y') > removing_date:
            print(filenames)
            # os.remove(filenames)