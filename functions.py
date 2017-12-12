import shutil
from datetime import datetime

def backup_db():
	now = datetime.now()
	shutil.copy('db.sqlite3', 'backup/{}.sqlite3'.format(now.strftime("%y-%m-%d_%H:%M:%S")))
