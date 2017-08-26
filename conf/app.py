import os

from .development import config as development_config
from .staging import config as staging_config
from .production import config as production_config

env = os.environ['PYTHON_ENV']

if env == "development":
    config = development_config
elif env == "staging":
    config = staging_config
elif env == "production":
    config = production_config