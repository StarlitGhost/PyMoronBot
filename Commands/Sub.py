# -*- coding: utf-8 -*-
"""
Created on Feb 28, 2015

@author: Tyranic-Moron
"""
import re

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

from twisted.words.protocols.irc import assembleFormattedText, attributes as A


class UnbalancedBracesException(Exception):
    def __init__(self, message, column):
        # Call the base exception constructor with the params it needs
        super(UnbalancedBracesException, self).__init__(message)
        # Store the column position of the unbalanced brace
        self.column = column


class Sub(CommandInterface):
    triggers = ['sub']
    help = "sub <text with subcommands> - fill this out when I figure out how best to explain it"
    runInThread = True

    def execute(self, message):
        """
        @type message: IRCMessage
        """

        subString = self._mangleEscapes(message.Parameters)

        try:
            segments = list(self._parseSubcommandTree(subString))
        except UnbalancedBracesException as e:
            red = assembleFormattedText(A.fg.lightRed[''])
            normal = assembleFormattedText(A.normal[''])
            error = subString[:e.column] + red + subString[e.column] + normal + subString[e.column+1:]
            error = self._unmangleEscapes(error, False)
            return [IRCResponse(ResponseType.Say, u"Sub Error: {}".format(e.message), message.ReplyTo),
                    IRCResponse(ResponseType.Say, error, message.ReplyTo)]

        prevLevel = -1
        responseStack = []

        for segment in segments:
            (level, command, start, end) = segment

            # We've finished executing subcommands at the previous depth,
            # so replace subcommands with their output at the current depth
            if level < prevLevel:
                command = self._substituteResponses(command, responseStack, start)

            # Build a new message out of this segment
            inputMessage = IRCMessage(message.Type, message.User.String, message.Channel,
                                      self.bot.commandChar + command.lstrip(),
                                      self.bot)

            # Execute the constructed message
            if inputMessage.Command.lower() in self.bot.moduleHandler.mappedTriggers:
                response = self.bot.moduleHandler.mappedTriggers[inputMessage.Command.lower()].execute(inputMessage)
                """@type : IRCResponse"""
            else:
                return IRCResponse(ResponseType.Say,
                                   u"'{}' is not a recognized command trigger".format(inputMessage.Command),
                                   message.ReplyTo)

            # Push the response onto the stack
            responseStack.append((response.Response, start, end))

            prevLevel = level

        responseString = self._substituteResponses(subString, responseStack, -1)
        responseString = self._unmangleEscapes(responseString)
        return IRCResponse(ResponseType.Say, responseString, message.ReplyTo)

    @staticmethod
    def _parseSubcommandTree(string):
        """Parse braced segments in string as tuples (level, contents, start index, end index)."""
        stack = []
        for i, c in enumerate(string):

            if c == '{':
                stack.append(i)
            elif c == '}':
                if stack:
                    start = stack.pop()
                    yield (len(stack), string[start + 1: i], start, i)
                else:
                    raise UnbalancedBracesException(u"unbalanced closing brace", i)

        if stack:
            start = stack.pop()
            raise UnbalancedBracesException(u"unbalanced opening brace", start)

    @staticmethod
    def _substituteResponses(command, responseStack, start):
        # Pop responses off the stack and replace the subcommand that generated them
        # Responses are popped in FILO order, so start & end positions of earlier subcommands are not affected
        while len(responseStack) > 0:
            responseString, rStart, rEnd = responseStack.pop()
            cStart = rStart - start - 1
            cEnd = rEnd - start
            # Replace the subcommand with its output
            command = command[:cStart] + responseString + command[cEnd:]

        return command

    @staticmethod
    def _mangleEscapes(string):
        # Replace escaped left and right braces with something that should never show up in messages/responses
        string = re.sub(r'(?<!\\)\\\{', '@LB@', string)
        string = re.sub(r'(?<!\\)\\\}', '@RB@', string)
        return string

    @staticmethod
    def _unmangleEscapes(string, unescape=True):
        if unescape:
            # Replace the mangled escaped braces with unescaped braces
            string = string.replace('@LB@', '{')
            string = string.replace('@RB@', '}')
        else:
            # Just unmangle them, ie, keep the escapes
            string = string.replace('@LB@', '\\{')
            string = string.replace('@RB@', '\\}')
        return string