# -*- coding: utf-8 -*-
"""
Created on May 10, 2014

@author: Tyranic-Moron
"""

import random
import operator
import collections
from builtins import range

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

import ply.lex as lex
import ply.yacc as yacc


MAX_DICE = 10000
MAX_SIDES = 10000


class UnknownCharacterException(Exception):
    pass

class SyntaxErrorException(Exception):
    pass

class TooManyDiceException(Exception):
    pass

class TooManySidesException(Exception):
    pass

class NegativeDiceException(Exception):
    pass

class NegativeSidesException(Exception):
    pass

class ZeroSidesException(Exception):
    pass


class Roll(CommandInterface):
    triggers = ['roll', 'rollv']
    help = 'roll(v) - dice roller, \'rollv\' outputs every roll. supported operators are NdN, dN, + - * / ^ ( ) #comments\n' \
           'example usage: rollv 5d6 + ((5d(2d10)) - d10) * (d20 / 5) #unnecessarily complicated roll\n' \
           'output: User rolled: [5d6: 3,1,5,4,4 (17) | 2d10: 5,3 (8) | 5d8: 5,1,3,7,2 (18) | 1d10: 7 (7) | 1d20: 4 (4)] 17'

    # noinspection PyUnusedLocal
    def onLoad(self):

        tokens = ('NUMBER',
                  'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EXPONENT', 'DICE',
                  'LPAREN', 'RPAREN', 'POINT')

        # Tokens

        t_PLUS = r'\+'
        t_MINUS = r'-'
        t_TIMES = r'\*'
        t_DIVIDE = r'/'
        t_EXPONENT = r'\^'
        t_DICE = r'd'
        t_LPAREN = r'\('
        t_RPAREN = r'\)'
        t_POINT = r'\.'

        def t_NUMBER(t):
            r"""\d+"""
            try:
                if len(t.value) < 100:
                    t.value = int(t.value)
                else:
                    raise ValueError
            except ValueError:
                t.value = 0
            return t

        # Ignored characters
        t_ignore = ' \t'

        def t_COMMENT(_):
            r"""\#.*"""
            pass
            # No return value. Token discarded

        # Calculate the column position of the given token.
        #     input is the input text string
        #     token is a token instance
        def findColumn(token):
            if token is not None:
                last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
                if last_cr < 0:
                    last_cr = 0
                column = (token.lexpos - last_cr) + 1
                return column
            else:
                return 'unknown'

        def t_error(t):
            col = findColumn(t)
            raise UnknownCharacterException(u"unknown character '{0}' (col {1})".format(t.value[0], col))

        self.lexer = lex.lex()

        # Parsing rules
        precedence = (('left', 'PLUS', 'MINUS'),
                      ('left', 'TIMES', 'DIVIDE'),
                      ('left', 'EXPONENT'),
                      ('left', 'DICE'),
                      ('right', 'UMINUS'),
                      ('right', 'UDICE'))

        def p_statement_expr(p):
            """statement : expression"""
            p[0] = p[1]

        def p_expression_binop(p):
            """expression : expression PLUS expression
                          | expression MINUS expression
                          | expression TIMES expression
                          | expression DIVIDE expression
                          | expression EXPONENT expression"""
            op = p[2]
            left = sumList(p[1])
            right = sumList(p[3])

            if op == '+':
                p[0] = operator.add(left, right)
            elif op == '-':
                p[0] = operator.sub(left, right)
            elif op == '*':
                p[0] = operator.mul(left, right)
            elif op == '/':
                p[0] = operator.floordiv(left, right)
            elif op == '^':
                p[0] = operator.pow(left, right)

        def p_expression_dice(p):
            """expression : expression DICE expression"""
            p[0] = rollDice(p[1], p[3])

        def p_expression_uminus(p):
            """expression : MINUS expression %prec UMINUS"""
            p[0] = operator.neg(sumList(p[2]))

        def p_expression_udice(p):
            """expression : DICE expression %prec UDICE"""
            p[0] = rollDice(1, p[2])

        def p_expression_group(p):
            """expression : LPAREN expression RPAREN"""
            p[0] = p[2]

        def p_expression_number(p):
            """expression : NUMBER"""
            p[0] = p[1]

        def p_error(p):
            if p is None:
                raise SyntaxErrorException(u"syntax error at the end of the given expression")

            col = findColumn(p)
            raise SyntaxErrorException(u"syntax error at '{0}' (col {1})".format(p.value, col))

        def rollDice(numDice, numSides):
            numDice = sumList(numDice)
            numSides = sumList(numSides)

            if numDice > MAX_DICE:
                raise TooManyDiceException(u'attempted to roll more than {0} dice in a single d expression'.format(MAX_DICE))
            if numSides > MAX_SIDES:
                raise TooManySidesException(u'attempted to roll a die with more than {0} sides'.format(MAX_SIDES))
            if numDice < 0:
                raise NegativeDiceException(u'attempted to roll a negative number of dice')
            if numSides < 0:
                raise NegativeSidesException(u'attempted to roll a die with a negative number of sides')
            if numSides < 1:
                raise ZeroSidesException(u'attempted to roll a die with zero sides')

            rolls = []
            for dice in range(0, numDice):
                rolls.append(random.randint(1, numSides))

            self.yaccer.rolls.append((u'{0}d{1}'.format(numDice, numSides), rolls))

            return rolls

        def sumList(rolls):
            if isinstance(rolls, collections.Iterable):
                return sum(rolls)
            else:
                return rolls

        self.yaccer = yacc.yacc()
        self.yaccer.rolls = []

    def execute(self, message):
        """
        @type message: IRCMessage
        """

        verbose = False
        if message.Command.lower().endswith('v'):
            verbose = True

        try:
            result = self.yaccer.parse(message.Parameters)
            if isinstance(result, collections.Iterable):
                result = sum(result)
        except OverflowError:
            self.yaccer.rolls = []

            return IRCResponse(ResponseType.Say,
                               u'Error: result too large to calculate',
                               message.ReplyTo)
        except (ZeroDivisionError,
                UnknownCharacterException,
                SyntaxErrorException,
                TooManyDiceException,
                TooManySidesException,
                NegativeDiceException,
                NegativeSidesException,
                ZeroSidesException) as e:
            self.yaccer.rolls = []

            return IRCResponse(ResponseType.Say,
                               u'Error: {0}'.format(e),
                               message.ReplyTo)

        rolls = self.yaccer.rolls
        self.yaccer.rolls = []

        if verbose:
            rollStrings = []
            for dice, rollList in rolls:
                rollStrings.append(u'{0}: {1} ({2})'.format(dice,
                                                            u','.join(u'{0}'.format(roll) for roll in rollList),
                                                            sum(rollList)))
            rollString = u' | '.join(rollStrings)

            if len(rollString) > 200:
                rollString = u"LOTS O' DICE"

            response = u'{0} rolled: [{1}] {2}'.format(message.User.Name, rollString, result)

        else:
            response = u'{0} rolled: {1}'.format(message.User.Name, result)

        return IRCResponse(ResponseType.Say, response, message.ReplyTo, {'rollTotal': result})
