# -*- coding: utf-8 -*-

import copy
from ruamel.yaml import YAML
from six import iteritems


_required = ['server']


class Config(object):
    def __init__(self, configFile):
        self.configFile = configFile
        self._configData = {}
        self.yaml = YAML()
        self._inBaseConfig = []

    def loadConfig(self):
        configData = self._readConfig(self.configFile)
        self._validate(configData)
        self._configData = configData

    def _readConfig(self, fileName):
        try:
            with open(fileName, mode='r') as config:
                configData = self.yaml.load(config)
                if not configData:
                    configData = {}
                # if this is the base server config, store what keys we loaded
                if fileName == self.configFile:
                    self._inBaseConfig = list(configData.keys())
        except Exception as e:
            raise ConfigError(fileName, e)

        if 'import' not in configData:
            return configData

        for fname in configData['import']:
            includeConfig = self._readConfig('configs/{}.yaml'.format(fname))
            for key, val in iteritems(includeConfig):
                # not present in base config, just assign it
                if key not in configData:
                    configData[key] = val
                    continue
                # skip non-collection types that are already set
                if isinstance(configData[key], (str, int)):
                    continue
                if isinstance(val, str):
                    raise ConfigError(fname, 'The included config file tried '
                                             'to merge a non-string with a '
                                             'string')
                try:
                    iter(configData[key])
                    iter(val)
                except TypeError:
                    # not a collection, so just don't merge them
                    pass
                else:
                    try:
                        # merge with + operator
                        configData[key] += val
                    except TypeError:
                        # dicts can't merge with +
                        try:
                            for subKey, subVal in iteritems(val):
                                if subKey not in configData[key]:
                                    configData[key][subKey] = subVal
                        except (AttributeError, TypeError):
                            # if either of these, they weren't both dicts.
                            raise ConfigError(fname, 'The variable {!r} could '
                                                     'not be successfully '
                                                     'merged'.format(key))

        return configData

    def writeConfig(self):
        # filter the configData to only those keys
        # that were present in the base server config,
        # or have been modified at runtime
        configData = copy.deepcopy(self._configData)
        to_delete = set(configData.keys()).difference(self._inBaseConfig)
        for key in to_delete:
            del configData[key]

        # write the filtered configData
        try:
            with open(self.configFile, mode='w') as config:
                self.yaml.dump(configData, config)
        except Exception as e:
            raise ConfigError(self.configFile, e)

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

    def __setitem__(self, key, value):
        # mark this key to be saved in the server config
        if key not in self._inBaseConfig:
            self._inBaseConfig.append(key)

        self._configData[key] = value

    def __contains__(self, key):
        return key in self._configData


class ConfigError(Exception):
    def __init__(self, configFile, message):
        self.configFile = configFile
        self.message = message

    def __str__(self):
        return 'An error occurred while reading config file {}: {}'.format(self.configFile,
                                                                           self.message)
