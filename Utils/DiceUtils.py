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

class OperandsTooLargeException(Exception):
    pass


class Die(object):
    def __init__(self, numSides):
        self.numSides = numSides
        self.value = random.randint(1, self.numSides)
        self.exploded = False
        self.dropped = False

    def __str__(self):
        value = str(self.value)
        if self.exploded:
            value = u'*{}*'.format(value)
        if self.dropped:
            value = u'-{}-'.format(value)

        return value

    def __lt__(self, other):
        return self.value < other.value


class RollList(object):
    def __init__(self, numDice, numSides):
        self.numDice = numDice
        self.numSides = numSides
        self.rolls = [Die(numSides) for _ in range(0, numDice)]

    def sum(self):
        return sum(r.value for r in self.rolls if not r.dropped)

    def __str__(self):
        return u'{}d{}: {} ({})'.format(self.numDice, self.numSides, u','.join(str(die) for die in self.rolls), self.sum())


class DiceParser(object):
    def __init__(self, maxDice=10000, maxSides=10000, maxExponent=10000):
        self._MAX_DICE = maxDice
        self._MAX_SIDES = maxSides
        self._MAX_EXPONENT = maxExponent

        self.lexer = lex.lex(module=self)
        self.yaccer = yacc.yacc(module=self)

        self.rolls = []
        self.description = None

    def reset(self):
        self.rolls = []
        self.description = None

    def parse(self, diceexpr):
        self.reset()

        result = self.yaccer.parse(diceexpr)
        result = self._sumDiceRolls(result)
        return result

    def getRollStrings(self):
        rollStrings = (str(roll) for roll in self.rolls)
        return rollStrings

    tokens = ('NUMBER',
              'PLUS', 'MINUS',
              'TIMES', 'DIVIDE',
              'EXPONENT',
              'KEEPHIGHEST', 'KEEPLOWEST', 'DROPHIGHEST', 'DROPLOWEST', 'EXPLODE',
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
    t_DROPHIGHEST = r'dh'
    t_DROPLOWEST = r'dl'
    t_EXPLODE = r'!'
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
        self.description = str(t.value)[1:].strip()

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
                  ('left', 'KEEPHIGHEST', 'KEEPLOWEST', 'DROPHIGHEST', 'DROPLOWEST', 'EXPLODE'),
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
            if -self._MAX_EXPONENT <= left <= self._MAX_EXPONENT and -self._MAX_EXPONENT <= right <= self._MAX_EXPONENT:
                p[0] = operator.pow(left, right)
            else:
                raise OperandsTooLargeException(u'operand or exponent is larger than the maximum {}'
                                                .format(self._MAX_EXPONENT))

    def p_expr_diceexpr(self, p):
        """expression : dice_expr"""
        p[0] = p[1]

    def p_dice_expr(self, p):
        """dice_expr : expression DICE expression"""
        p[0] = self._rollDice(p[1], p[3])

    def p_explode_expr(self, p):
        """dice_expr : dice_expr EXPLODE expression
                     | dice_expr EXPLODE"""
        rollList = p[1]
        threshold = rollList.numSides

        if len(p) > 3:
            threshold = p[3]

        debrisDice = []
        for roll in rollList.rolls:
            if roll.value >= threshold:
                index = rollList.rolls.index(roll)
                rollList.rolls[index].exploded = True

                debrisDice.append(Die(roll.numSides))

        rollList.rolls.extend(debrisDice)

        p[0] = rollList

    def p_keepdrop_expr(self, p):
        """dice_expr : dice_expr KEEPHIGHEST expression
                     | dice_expr KEEPLOWEST expression
                     | dice_expr DROPHIGHEST expression
                     | dice_expr DROPLOWEST expression
                     | dice_expr KEEPHIGHEST
                     | dice_expr KEEPLOWEST
                     | dice_expr DROPHIGHEST
                     | dice_expr DROPLOWEST"""
        rollList = p[1]
        op = p[2]
        if len(p) > 3:
            keepDrop = self._sumDiceRolls(p[3])
        else:
            # default to 1 if no right arg was given
            keepDrop = 1

        # filter dice that have already been dropped
        validRolls = [r for r in rollList.rolls if not r.dropped]

        # if it's a drop op, invert the number into a keep count
        if op.startswith('d'):
            opType = 'drop'
            keepDrop = len(validRolls) - keepDrop
        else:
            opType = 'keep'

        if len(validRolls) < keepDrop:
            raise NotEnoughDiceException(u'attempted to {} {} dice when only {} were rolled'.format(opType,
                                                                                                    keepDrop,
                                                                                                    len(validRolls)))

        if op == 'kh' or op == 'dl':
            keptRolls = heapq.nlargest(keepDrop, validRolls)
        elif op == 'kl' or op == 'dh':
            keptRolls = heapq.nsmallest(keepDrop, validRolls)
        else:
            raise NotImplementedError(u"operator '{}' is not implemented (also, this should be impossible?)")

        # determine which rolls were dropped, and mark them as such
        dropped = list((mset(validRolls) - mset(keptRolls)).elements())
        for drop in dropped:
            index = rollList.rolls.index(drop)
            rollList.rolls[index].dropped = True

        p[0] = rollList

    def p_expression_uminus(self, p):
        """expression : MINUS expression %prec UMINUS"""
        p[0] = operator.neg(self._sumDiceRolls(p[2]))

    def p_expression_udice(self, p):
        """dice_expr : DICE expression %prec UDICE"""
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
            raise OperandsTooLargeException(u'attempted to roll more than {} dice in a single d expression'
                                            .format(self._MAX_DICE))
        if numSides > self._MAX_SIDES:
            raise OperandsTooLargeException(u'attempted to roll a die with more than {} sides'
                                            .format(self._MAX_SIDES))
        if numDice < 0:
            raise NegativeDiceException(u'attempted to roll a negative number of dice')
        if numSides < 0:
            raise NegativeSidesException(u'attempted to roll a die with a negative number of sides')
        if numSides < 1:
            raise ZeroSidesException(u'attempted to roll a die with zero sides')

        return RollList(numDice, numSides)

    def _sumDiceRolls(self, rollList):
        """convert from dice roll structure to a single integer result"""
        if isinstance(rollList, RollList):
            self.rolls.append(rollList)
            return rollList.sum()
        else:
            return rollList


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
        return
    except (ZeroDivisionError,
            UnknownCharacterException,
            SyntaxErrorException,
            OperandsTooLargeException,
            NegativeDiceException,
            NegativeDiceException,
            ZeroSidesException,
            NotEnoughDiceException,
            NotImplementedError) as e:
        print(u'Error: {}'.format(e))
        return

    if roller.description:
        result = u'{} {}'.format(result, roller.description)

    if cmdArgs.verbose:
        rollStrings = roller.getRollStrings()
        rollString = u' | '.join(rollStrings)

        print('[{}] {}'.format(rollString, result))
        return

    print(result)


if __name__ == '__main__':
    main()
