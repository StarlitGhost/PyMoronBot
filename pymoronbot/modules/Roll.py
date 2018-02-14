# -*- coding: utf-8 -*-
"""
Created on May 10, 2014

@author: Tyranic-Moron
"""

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.moduleinterface import ModuleInterface
from pymoronbot.utils import dice


class Roll(ModuleInterface):
    triggers = ['roll', 'rollv']
    help = 'roll(v) - dice roller, \'rollv\' outputs every roll. supported operators are #d#(kh#/kl#/dh#/dl#/!/r/ro/s/sa/sd), + - * / % ^ ( ) #comments | ' \
           'see https://git.io/PyMoBo-Roll for example usage and a detailed explanation of the dice modifiers'

    def onLoad(self):
        self.roller = dice.DiceParser()

    def execute(self, message):
        """
        @type message: IRCMessage
        """

        verbose = False
        if message.Command.lower().endswith('v'):
            verbose = True

        try:
            result = self.roller.parse(message.Parameters)
        except OverflowError:
            return IRCResponse(ResponseType.Say,
                               u'Error: result too large to calculate',
                               message.ReplyTo)
        except (ZeroDivisionError,
                dice.UnknownCharacterException,
                dice.SyntaxErrorException,
                dice.InvalidOperandsException,
                RecursionError,
                NotImplementedError) as e:
            return IRCResponse(ResponseType.Say,
                               u'Error: {}'.format(e),
                               message.ReplyTo)

        if verbose:
            rollStrings = self.roller.getRollStrings()
            rollString = u' | '.join(rollStrings)

            if len(rollString) > 200:
                rollString = u"LOTS O' DICE"

            response = u'{} rolled: [{}] {}'.format(message.User.Name, rollString, result)

        else:
            response = u'{} rolled: {}'.format(message.User.Name, result)

        if self.roller.description:
            response += u' {}'.format(self.roller.description)

        return IRCResponse(ResponseType.Say, response, message.ReplyTo, {'rollTotal': result})
