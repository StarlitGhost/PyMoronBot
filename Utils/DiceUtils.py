# -*- coding: utf-8 -*-
"""
Created on Feb 01, 2018

@author: Tyranic-Moron
"""

import random
import operator
import collections
from builtins import range
import heapq
from collections import Counter as mset

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc


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

class NotEnoughDiceException(Exception):
    pass


class DiceParser(object):

    def __init__(self, maxDice=10000, maxSides=10000):
        self._MAX_DICE = maxDice
        self._MAX_SIDES = maxSides

        self.lexer = lex.lex(module=self)
        self.yaccer = yacc.yacc(module=self)

        self.rolls = []

    def parse(self, diceexpr):
        self.rolls = []

        result = self.yaccer.parse(diceexpr)
        if isinstance(result, collections.Iterable):
            result = self._sumDiceRolls(result)
        return result

    def getRollStrings(self):
        rollStrings = []
        for diceRoll in self.rolls:
            rollStrings.append(u'{}d{}: {} ({})'.format(diceRoll['numDice'], diceRoll['numSides'],
                                                        u','.join(u'{}'.format(roll) for roll in diceRoll['rolls']),
                                                        sum(r for r in diceRoll['rolls'] if isinstance(r, int))))
        return rollStrings

    tokens = ('NUMBER',
              'PLUS', 'MINUS',
              'TIMES', 'DIVIDE',
              'EXPONENT',
              'KEEPHIGHEST', 'KEEPLOWEST',
              'DICE',
              'LPAREN', 'RPAREN',
              'POINT')

    # Tokens

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EXPONENT = r'\^'
    t_KEEPHIGHEST = r'kh'
    t_KEEPLOWEST = r'kl'
    t_DICE = r'd'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_POINT = r'\.'

    @TOKEN(r'\d+')
    def t_NUMBER(self, t):
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

    @TOKEN(r'\#.*')
    def t_COMMENT(self, t):
        pass
        # No return value. Token discarded

    # Calculate the column position of the given token.
    #     input is the input text string
    #     token is a token instance
    def _findColumn(self, token):
        if token is not None:
            last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
            if last_cr < 0:
                last_cr = 0
            column = (token.lexpos - last_cr) + 1
            return column
        else:
            return 'unknown'

    def t_error(self, t):
        col = self._findColumn(t)
        raise UnknownCharacterException(u"unknown character '{}' (col {})".format(t.value[0], col))

    # Parsing rules
    precedence = (('left', 'PLUS', 'MINUS'),
                  ('left', 'TIMES', 'DIVIDE'),
                  ('left', 'EXPONENT'),
                  ('left', 'KEEPHIGHEST', 'KEEPLOWEST'),
                  ('left', 'DICE'),
                  ('right', 'UMINUS'),
                  ('right', 'UDICE'))

    def p_statement_expr(self, p):
        """statement : expression"""
        p[0] = p[1]

    def p_expression_binop(self, p):
        """expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression
                      | expression EXPONENT expression"""

        op = p[2]
        left = self._sumDiceRolls(p[1])
        right = self._sumDiceRolls(p[3])

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

    def p_expr_diceexpr(self, p):
        """expression : dice_expr"""
        p[0] = p[1]

    def p_dice_expr(self, p):
        """dice_expr : expression DICE expression"""
        p[0] = self._rollDice(p[1], p[3])

    def p_keep_expr(self, p):
        """dice_expr : dice_expr KEEPHIGHEST expression
                     | dice_expr KEEPLOWEST expression"""
        rolls = p[1]
        op = p[2]
        keep = self._sumDiceRolls(p[3])

        if len(rolls) < keep:
            raise NotEnoughDiceException(u'attempted to keep {} dice when only {} were rolled'.format(keep, len(rolls['rolls'])))

        if op == 'kh':
            keptRolls = heapq.nlargest(keep, rolls['rolls'])
        elif op == 'kl':
            keptRolls = heapq.nsmallest(keep, rolls['rolls'])

        dropped = list((mset(rolls['rolls']) - mset(keptRolls)).elements())
        for drop in dropped:
            index = rolls['rolls'].index(drop)
            rolls['rolls'][index] = u'-{}-'.format(drop)

        p[0] = rolls

    def p_expression_uminus(self, p):
        """expression : MINUS expression %prec UMINUS"""
        p[0] = operator.neg(self._sumDiceRolls(p[2]))

    def p_expression_udice(self, p):
        """expression : DICE expression %prec UDICE"""
        p[0] = self._rollDice(1, p[2])

    def p_expression_group(self, p):
        """expression : LPAREN expression RPAREN"""
        p[0] = p[2]

    def p_expression_number(self, p):
        """expression : NUMBER"""
        p[0] = p[1]

    def p_error(self, p):
        if p is None:
            raise SyntaxErrorException(u"syntax error at the end of the given expression")

        col = self._findColumn(p)
        raise SyntaxErrorException(u"syntax error at '{}' (col {})".format(p.value, col))

    def _rollDice(self, numDice, numSides):
        numDice = self._sumDiceRolls(numDice)
        numSides = self._sumDiceRolls(numSides)

        if numDice > self._MAX_DICE:
            raise TooManyDiceException(u'attempted to roll more than {} dice in a single d expression'.format(self._MAX_DICE))
        if numSides > self._MAX_SIDES:
            raise TooManySidesException(u'attempted to roll a die with more than {} sides'.format(self._MAX_SIDES))
        if numDice < 0:
            raise NegativeDiceException(u'attempted to roll a negative number of dice')
        if numSides < 0:
            raise NegativeSidesException(u'attempted to roll a die with a negative number of sides')
        if numSides < 1:
            raise ZeroSidesException(u'attempted to roll a die with zero sides')

        rolls = []
        for dice in range(0, numDice):
            rolls.append(random.randint(1, numSides))

        return {
            'numDice': numDice,
            'numSides': numSides,
            'rolls': rolls
        }

    def _sumDiceRolls(self, diceRolls):
        if isinstance(diceRolls, collections.Iterable):
            self.rolls.append(diceRolls)
            return sum(r for r in diceRolls['rolls'] if isinstance(r, int))
        else:
            return diceRolls


def main():
    import argparse
    argparser = argparse.ArgumentParser(description='An interpreter for dice expressions.')
    argparser.add_argument('-v', '--verbose', help='print all roll results', action='store_true')
    argparser.add_argument('diceexpr', help='the dice expression you want to execute', type=str)
    cmdArgs = argparser.parse_args()

    roller = DiceParser()

    try:
        result = roller.parse(cmdArgs.diceexpr)
    except OverflowError:
        print(u'Error: result too large to calculate')
    except (ZeroDivisionError,
            UnknownCharacterException,
            SyntaxErrorException,
            TooManyDiceException,
            TooManySidesException,
            NegativeDiceException,
            NegativeDiceException,
            ZeroSidesException) as e:
        print(u'Error: {}'.format(e))

    if cmdArgs.verbose:
        rolls = roller.rolls
        rollStrings = roller.getRollStrings()
        rollString = u' | '.join(rollStrings)

        print('[{}] {}'.format(rollString, result))
        return

    print(result)


if __name__ == '__main__':
    main()
