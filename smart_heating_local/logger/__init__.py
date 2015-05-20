import logging
import os

from smart_heating_local.config import Config

log_file = os.path.join(Config.PROJECT_ROOT, 'logs', 'smart-heating.log')

logging_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format)
# logging.basicConfig(filename='upload.log', level=logging.INFO, format=logging_format)

class NoRequestsModuleFilter(logging.Filter):
    def filter(self, record):
        return not record.name.startswith('requests.packages.urllib3.connectionpool')


log_formatter = logging.Formatter(logging_format)
root_logger = logging.getLogger()

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(log_formatter)
file_handler.addFilter(NoRequestsModuleFilter())
root_logger.addHandler(file_handler)
