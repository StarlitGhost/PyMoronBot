# -*- coding: utf-8 -*-
"""
Created on Dec 07, 2014

@author: Tyranic-Moron
"""

from CommandInterface import CommandInterface

from twisted.conch.manhole_tap import makeService
import os


class Manhole(CommandInterface):
    help = "A debug module that uses Twisted's Manhole to poke at the bot's innards"
    runInThread = True

    manhole = None

    def onLoad(self):
        self.manhole = makeService({
            "namespace": {"bot": self.bot},
            "passwd": os.path.join("Data", "manhole.passwd"),
            "telnetPort": "4141",
            "sshPort": "4040"
        })
        self.manhole.startService()

    def onUnload(self):
        self.manhole.stopService()
