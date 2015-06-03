from logging import *
import os

from smart_heating_local.config import Config

log_file = os.path.join(Config.PROJECT_ROOT, 'logs', 'smart-heating.log')

logging_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
basicConfig(level=INFO, format=logging_format)
# logging.basicConfig(filename='upload.log', level=logging.INFO, format=logging_format)

class NoRequestsModuleFilter(Filter):
    def filter(self, record):
        return not record.name.startswith('requests.packages.urllib3.connectionpool')


log_formatter = Formatter(logging_format)
root_logger = getLogger()

file_handler = FileHandler(log_file)
file_handler.setFormatter(log_formatter)
file_handler.addFilter(NoRequestsModuleFilter())
root_logger.addHandler(file_handler)
