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
    help = 'roll(v) - dice roller, \'rollv\' outputs every roll. supported operators are NdN, dN, + - * / ^ ( ) #comments\n' \
           'example usage: rollv 5d6 + ((5d(2d10)) - d10) * (d20 / 5) #unnecessarily complicated roll\n' \
           'output: User rolled: [5d6: 3,1,5,4,4 (17) | 2d10: 5,3 (8) | 5d8: 5,1,3,7,2 (18) | 1d10: 7 (7) | 1d20: 4 (4)] 17'

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

        return IRCResponse(ResponseType.Say, response, message.ReplyTo, {'rollTotal': result})
