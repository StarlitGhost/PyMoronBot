# -*- coding: utf-8 -*-
from twisted.plugin import pluginPackagePaths
import os


# From txircd:
# https://github.com/ElementalAlchemist/txircd/blob/8832098149b7c5f9b0708efe5c836c8160b0c7e6/txircd/modules/__init__.py
__path__.extend(pluginPackagePaths(__name__))
for directory, subdirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
    for subdir in subdirs:
        __path__.append(os.path.join(directory, subdir)) # Include all module subdirectories in the path
__all__ = []
