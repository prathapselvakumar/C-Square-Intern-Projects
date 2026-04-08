import sys
sys.path.insert(0, '/var/www/html/python/py-hr-connect-bot')
from app import app as application
application.secret_key='vkey'
