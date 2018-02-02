# -*- coding: utf-8 -*-
"""
Created on May 10, 2014

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from Utils import DiceUtils


class Roll(CommandInterface):
    triggers = ['roll', 'rollv']
    help = 'roll(v) - dice roller, \'rollv\' outputs every roll. supported operators are #d#(kh#/kl#/dh#/dl#), + - * / ^ ( ) #comments\n' \
           'example usage: rollv 5d6 + (5d(2d10)dl1 - d10) * (d20 / 5) #unnecessarily complicated roll\n' \
           'output: User rolled: [2d10: 4,3 (7) | 5d7: 7,3,-1-,4,7 (21) | 1d10: 1 (1) | 1d20: 12 (12) | 5d6: 3,6,2,4,6 (21)] 61 unnecessarily complicated roll'

    # noinspection PyUnusedLocal
    def onLoad(self):
        self.roller = DiceUtils.DiceParser()

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
                DiceUtils.UnknownCharacterException,
                DiceUtils.SyntaxErrorException,
                DiceUtils.TooManyDiceException,
                DiceUtils.TooManySidesException,
                DiceUtils.NegativeDiceException,
                DiceUtils.NegativeSidesException,
                DiceUtils.ZeroSidesException,
                DiceUtils.NotEnoughDiceException) as e:
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
