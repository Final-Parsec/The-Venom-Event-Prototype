from networking.server.database import MemoryDatabase
from os import makedirs
from os.path import exists

import logging
import time


# SERVER CONFIGURATION
HOST = 'localhost'
LOG_DIRECTORY = 'C:/snakes_server_logs/'
PORT = 9999

# engines and data for use throughout
memory_database = MemoryDatabase()

# set up logging
if not exists(LOG_DIRECTORY):
    makedirs(LOG_DIRECTORY)

log_file_path = LOG_DIRECTORY + time.strftime('%Y%m%d-%H%M%S.txt')
logging.basicConfig(filename=log_file_path, level=logging.WARNING)

# We do this so decorators on controller functions get called, assigning message handlers for the request handler.
from networking.server.controllers import *