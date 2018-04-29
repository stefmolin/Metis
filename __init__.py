import time
import os
import logging
import argparse
import yaml
import signal
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base() # this needs to be here (can't move)

from flask import Flask
app = Flask(__name__)
app.secret_key = 'Esto es un secreto'

# Logging configuration
FORMAT = '[%(levelname)s] [ %(name)s ] %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(os.path.basename(__file__))

# determine where to run the app with optional command line argument
parser = argparse.ArgumentParser()
parser.add_argument("--test_locally", nargs='?', help="Run the app on local machine connecting to a database that is already created.")
args = parser.parse_args()

db_config_file = 'db_config.yml'

if args.test_locally:
  with open('local_' + db_config_file, 'r') as yaml_file:
    db_info = yaml.load(yaml_file)
else:
  # running inside Docker container
  with open(db_config_file, 'r') as yaml_file:
    db_info = yaml.load(yaml_file)

db_username = db_info['username']
db_password = db_info['password']
db_host = db_info['host']
db_port = db_info['port']

from metis.database import MetisDatabase
# needs to be declared outside the if __name__ == '__main__'
metis_db = MetisDatabase(db_uri="postgresql://{user}:{password}@{db}:{db_port}".\
  format(user=db_username, password=db_password, db=db_host, db_port=db_port), \
  base=Base)

from metis import webapp # needs to be after the MetisDatabase stuff

if __name__ == "__main__":
  def handler(signum, frame):
    logger.info("SIGTERM received")
    # close out connections
    metis_db.close_connections()
    logger.info("Cleanup complete")

  signal.signal(signal.SIGTERM, handler)

  # starting app (accessible externally through port 5000)
  logger.info('Launching the web app.')
  app.run(host='0.0.0.0', port=5000)

  # locally close out connections
  if args.test_locally:
      metis_db.close_connections()
