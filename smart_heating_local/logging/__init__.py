"""
Copyright 2016 Michael Spiegel, Wilhelm Kleiminger

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from logging import *
import os

from smart_heating_local.config import Config

log_file = os.path.join(Config.PROJECT_ROOT, 'logs', 'smart-heating.log')

logging_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
basicConfig(level=INFO, format=logging_format)

class NoRequestsModuleFilter(Filter):
    def filter(self, record):
        return not record.name.startswith('requests.packages.urllib3.connectionpool')


log_formatter = Formatter(logging_format)
root_logger = getLogger()

file_handler = FileHandler(log_file)
file_handler.setFormatter(log_formatter)
file_handler.addFilter(NoRequestsModuleFilter())
root_logger.addHandler(file_handler)
