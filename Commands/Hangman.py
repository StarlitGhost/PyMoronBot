# -*- coding: utf-8 -*-
"""
Created on Jan 23, 2017

@author: Tyranic-Moron
"""

import random
import re
from collections import OrderedDict

import GlobalVars
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

from twisted.words.protocols.irc import assembleFormattedText, attributes as A


class AlreadyGuessedException(Exception):
    def __init__(self, letter):
        self.letter = letter
        self.message = u"the letter '{}' has already been guessed".format(letter)


class WrongPhraseLengthException(Exception):
    def __init__(self, guessedLen, phraseLen):
        self.guessedLen = guessedLen
        self.phraseLen = phraseLen
        self.message = u"your guess is {} letters, but the target is {} letters long".format(guessedLen, phraseLen)


class PhraseMismatchesGuessesException(Exception):
    def __init__(self):
        self.message = u"your guess does not match the revealed letters"


class GameState(object):
    def __init__(self, phrase, maxBadGuesses):
        self.phrase = phrase
        self.guesses = []
        self.badGuesses = 0
        self.maxBadGuesses = maxBadGuesses
        self.finished = False

    def guessLetter(self, letter):
        letter = letter.lower()
        if letter in self.guesses:
            raise AlreadyGuessedException(letter)

        self.guesses.append(letter)

        if self._renderMaskedPhrase() == self.phrase:
            self.finished = True

        if letter not in self.phrase:
            self._incrementBadGuesses()
            return False
        else:
            return True

    def guessPhrase(self, phrase):
        phrase = phrase.lower()
        if not len(phrase) == len(self.phrase):
            raise WrongPhraseLengthException(len(phrase), len(self.phrase))

        maskedPhrase = self._renderMaskedPhrase()
        for i, c in enumerate(maskedPhrase):
            if c == u'_':
                continue
            if phrase[i] != maskedPhrase[i]:
                raise PhraseMismatchesGuessesException()

        if phrase == self.phrase:
            for c in self.phrase:
                if c not in self.guesses:
                    self.guesses.append(c)
            self.finished = True
            return True
        else:
            self._incrementBadGuesses()
            return False

    def wOrP(self):
        if u' ' in self.phrase:
            return u'phrase'
        else:
            return u'word'

    def render(self):
        return u'{} {} {} {}'.format(
                self._renderMaskedPhrase(),
                self._renderPhraseLen(),
                self._renderBadGuessIndicator(),
                self._renderGuesses())

    def _renderMaskedPhrase(self):
        maskedPhrase = [
            c if c == u' ' or c in self.guesses
            else u'␣'
            for c in self.phrase
        ]
        return u''.join(maskedPhrase)

    def _renderPhraseLen(self):
        return u'({})'.format(len(self.phrase))

    def _renderBadGuessIndicator(self):
        trail = []

        for pos in xrange(self.maxBadGuesses):
            if pos - self.badGuesses == 0:
                # spark
                trail.append(u'*')
            elif pos - self.badGuesses < 0:
                # bad guesses
                trail.append(u'.')
            else:
                # guesses remaining
                trail.append(u'-')

        if self.badGuesses != self.maxBadGuesses:
            bomb = u'O'
        else:
            bomb = u'#'

        return u'[{}{}]'.format(u''.join(trail), bomb)

    def _renderGuesses(self):
        colouredGuesses = []
        for g in self.guesses:
            if g in self.phrase:
                g = g.encode('utf-8')
                colouredGuesses.append(assembleFormattedText(A.fg.green[g]))
            else:
                g = g.encode('utf-8')
                colouredGuesses.append(assembleFormattedText(A.fg.red[g]))
        reset = assembleFormattedText(A.normal[''])
        colouredGuesses = [c.decode(encoding='utf-8', errors='ignore') for c in colouredGuesses]
        return u'[{}{}]'.format(u''.join(colouredGuesses), reset)

    def _incrementBadGuesses(self):
        self.badGuesses += 1
        if self.badGuesses == self.maxBadGuesses:
            self.finished = True


class PhraseList(object):
    def __init__(self):
        self.dataPath = 'Data/hangman.txt'
        self.phraseList = self._loadPhrases()
        random.shuffle(self.phraseList)
        self.phraseGenerator = (p for p in self.phraseList)

    def shuffle(self):
        random.shuffle(self.phraseList)
        self.phraseGenerator = (p for p in self.phraseList)

    def getWord(self):
        try:
            return next(self.phraseGenerator)
        except StopIteration:
            self.shuffle()

    def _loadPhrases(self):
        try:
            with open(self.dataPath, 'r') as f:
                return [unicode(line.rstrip()) for line in f]
        except IOError:
            return [u'hangman.txt is missing!']

    def _savePhrases(self):
        with open(self.dataPath, 'w') as f:
            f.writelines(sorted(self.phraseList))


class Hangman(CommandInterface):
    triggers = ['hangman', 'hm']

    def onLoad(self):
        self._helpText = u"{1}hangman ({0}/<letter>/<phrase>) - plays games of hangman in the channel. "\
                         u"Use '{1}help hangman <subcommand>' for subcommand help.".format(
            u'/'.join(self.subCommands.keys()), self.bot.commandChar)
        self.gameStates = {}
        self.phraseList = PhraseList()
        self.maxBadGuesses = 8
    
    def _start(self, message):
        """start - starts a game of hangman!"""
        channel = message.ReplyTo.lower()
        if channel in self.gameStates:
            return [IRCResponse(ResponseType.Say,
                                u'[Hangman] game is already in progress!',
                                channel),
                    IRCResponse(ResponseType.Say,
                                self.gameStates[channel].render(),
                                message.ReplyTo)]

        responses = []

        word = self.phraseList.getWord()
        self.gameStates[channel] = GameState(word, self.maxBadGuesses)
        responses.append(IRCResponse(ResponseType.Say,
                                     u'[Hangman] started!',
                                     message.ReplyTo))
        responses.append(IRCResponse(ResponseType.Say,
                                     self.gameStates[channel].render(),
                                     message.ReplyTo))

        return responses

    def _stop(self, message, suppressMessage=False):
        """stop - stops the current game. Bot-admin only"""
        if not suppressMessage:
            if message.User.Name not in GlobalVars.admins:
                return IRCResponse(ResponseType.Say,
                                   u'[Hangman] only my admins can stop games!',
                                   message.ReplyTo)
        channel = message.ReplyTo.lower()
        if channel in self.gameStates:
            del self.gameStates[channel]
            if not suppressMessage:
                return IRCResponse(ResponseType.Say,
                                   u'[Hangman] game stopped!',
                                   message.ReplyTo)

    def _setMaxBadGuesses(self, message):
        """max <num> - sets the maximum number of bad guesses allowed in future games. Must be between 1 and 20. \
        Bot-admin only"""
        if message.User.Name in GlobalVars.admins:
            try:
                maxBadGuesses = int(message.ParameterList[1])
                if 0 < maxBadGuesses < 21:
                    response = u'[Hangman] maximum bad guesses changed from {} to {}'.format(self.maxBadGuesses,
                                                                                             maxBadGuesses)
                    self.maxBadGuesses = maxBadGuesses
                    return IRCResponse(ResponseType.Say, response, message.ReplyTo)
                else:
                    raise ValueError
            except ValueError:
                return IRCResponse(ResponseType.Say,
                                   u'[Hangman] maximum bad guesses should be an integer between 1 and 20',
                                   message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say,
                               u'[Hangman] only my admins can set the maximum bad guesses!',
                               message.ReplyTo)

    def _guess(self, message):
        """
        @type message: IRCMessage
        @rtype: IRCResponse
        """
        channel = message.ReplyTo.lower()
        if channel not in self.gameStates:
            return IRCResponse(ResponseType.Say,
                               u'[Hangman] no game running, use {}hangman start to begin!'.format(self.bot.commandChar),
                               message.ReplyTo)

        responses = []
        gs = self.gameStates[channel]

        guess = message.Parameters.lower()
        # single letter
        if len(guess) == 1:
            try:
                correct = gs.guessLetter(guess)
            except AlreadyGuessedException as e:
                return self._exceptionFormatter(e, message.ReplyTo)
        # whole phrase
        else:
            try:
                correct = gs.guessPhrase(guess)
            except WrongPhraseLengthException as e:
                return self._exceptionFormatter(e, message.ReplyTo)
            except PhraseMismatchesGuessesException as e:
                return self._exceptionFormatter(e, message.ReplyTo)

        user = message.User.Name
        if correct:
            colUser = assembleFormattedText(A.normal[A.fg.green[user]])
        else:
            colUser = assembleFormattedText(A.normal[A.fg.red[user]])
        responses.append(IRCResponse(ResponseType.Say,
                                     u'{} - {}'.format(gs.render(), colUser),
                                     message.ReplyTo))

        if gs.finished:
            if correct:
                responses.append(IRCResponse(ResponseType.Say,
                                             u'[Hangman] Congratulations {}!'.format(user),
                                             message.ReplyTo))
            else:
                responses.append(IRCResponse(ResponseType.Say,
                                             u'[Hangman] {} blew up the bomb! The {} was {}'.format(user,
                                                                                                    gs.wOrP(),
                                                                                                    gs.phrase),
                                             message.ReplyTo))
            self._stop(message, suppressMessage=True)

        return responses

    @staticmethod
    def _exceptionFormatter(exception, target):
        return IRCResponse(ResponseType.Say, u'[Hangman] {}'.format(exception.message), target)

    subCommands = OrderedDict([
        (u'start', _start),
        (u'stop', _stop),
        (u'max', _setMaxBadGuesses),
    ])

    def help(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 1:
            return self._helpText

        subCommand = message.ParameterList[1].lower()
        if subCommand in self.subCommands:
            if getattr(self.subCommands[subCommand], '__doc__'):
                docstring = self.subCommands[subCommand].__doc__
                docstring = re.sub(ur'\s+', u' ', docstring)
                return u'{1}hangman {0}'.format(docstring, self.bot.commandChar)
            else:
                return u"Oops! The help text for 'hangman {}' seems to be missing. "\
                       u"Tell my owner Tyranic-Moron!".format(subCommand)
        else:
            return self._helpText

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 0:
            return self._start(message)

        subCommand = message.ParameterList[0].lower()
        if subCommand in self.subCommands:
            return self.subCommands[subCommand](self, message)
        else:
            return self._guess(message)
