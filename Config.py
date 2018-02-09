# -*- coding: utf-8 -*-

import yaml


_required = [
    'address',
]


class Config(object):
    def __init__(self, configFile):
        self.configFile = configFile
        self._configData = {}

    def readConfig(self):
        try:
            with open(self.configFile, 'r') as config:
                configData = yaml.safe_load(config)
                if not configData:
                    configData = {}
        except Exception as e:
            raise ConfigError(self.ConfigFile, e)

        self._configData = configData

    def writeConfig(self):
        pass

    def getWithDefault(self, key, default=None):
        if key in self._configData:
            return self._configData[key]
        return default

    def _validate(self, configData):
        for key in _required:
            if key not in configData:
                raise ConfigError(self.configFile, 'Required item {!r} was not found in the config.'.format(key))

    def __len__(self):
        return len(self._configData)

    def __iter__(self):
        return iter(self._configData)

    def __getitem__(self, key):
        return self._configData[key]

    def __contains__(self, key):
        return key in self._configData


class ConfigError(Exception):
    def __init__(self, configFile, message):
        self.configFile = configFile
        self.message = message

    def __str__(self):
        return 'An error occurred while reading config file {}: {}'.format(self.configFile,
                                                                           self.message)
