"""
Start the web server.

$ python3 run.py --debug --port 8008
"""

import argparse
import json

from annotation_tools.annotation_tools import *
from threading import *
import time
from pymongo import MongoClient
from annotation_tools import default_config as cfg

DEFAULT_PORT = 8003
DEFAULT_HOST = '127.0.0.1'

def parse_args():

  parser = argparse.ArgumentParser(description='Visipedia Annotation Toolkit')

  parser.add_argument('--debug', dest='debug',
                        help='Run in debug mode.',
                        required=False, action='store_true', default=False)

  parser.add_argument('--port', dest='port',
                        help='Port to run on.', type=int,
                        required=False, default=DEFAULT_PORT)

  parser.add_argument('--host', dest='host',
                        help='Host to run on, set to 0.0.0.0 for remote access', type=str,
                        required=False, default=DEFAULT_HOST)

  args = parser.parse_args()
  return args


# every 1 hr turn img 'annotating' from true to false
class UpdateAnnotating(Thread):
    def __init__(self, db):
        ''' Constructor. '''
        Thread.__init__(self)
        self.db = db
 
 
    def run(self):
        while(True):
          time.sleep(300)
          print ('Open annotating permission.')
          bulk = self.db.image.initialize_unordered_bulk_op();
          bulk.find( { 'annotating': True } ).update( { '$set': { 'annotating': False } } );
          bulk.execute();
          


def main():
  args = parse_args()

  client = MongoClient('mongodb://'+cfg.MONGO_HOST+':'+str(cfg.MONGO_PORT)+'/')
  db = client[cfg.MONGO_DBNAME]
 
  t1 = UpdateAnnotating(db)
 
  # Start running the threads!
  t1.start()
  
  app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
  main()

