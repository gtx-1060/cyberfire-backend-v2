import os
from typing import Optional

from dotenv import load_dotenv


class _VariablesLoader:
    __variables = \
        {
            'DB_USER': "",
            'DB_PASSWORD': "",
            'DB_HOST': "",
            'DB_NAME': "",

            'HOST': "",
            'PORT': "",

            "SECRET_KEY": "",
            "ALLOW_ORIGINS": ""
        }

    def __init__(self):
        load_dotenv()
        for key in self.__variables.keys():
            self.__variables[key] = os.getenv(key) or ""

    def get_variables(self):
        return self.__variables

    def __getitem__(self, item):
        return self.__variables[item]


env_vars = _VariablesLoader()
