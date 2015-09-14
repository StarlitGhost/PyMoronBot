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


class DictMergeError(Exception):
    pass


class Sub(CommandInterface):
    triggers = ['sub']
    help = "sub <text> - executes nested commands in <text> and replaces the commands with their output\n" \
           "syntax: text {command params} more text {command {command params} {command params}}\n" \
           "example: .sub Some {rainbow magical} {flip topsy-turvy} text"
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
        extraVars = {}
        metadata = {}

        for segment in segments:
            (level, command, start, end) = segment

            # We've finished executing subcommands at the previous depth,
            # so replace subcommands with their output at the current depth
            if level < prevLevel:
                command = self._substituteResponses(command, responseStack, level, extraVars, start)

            # Build a new message out of this segment
            inputMessage = IRCMessage(message.Type, message.User.String, message.Channel,
                                      self.bot.commandChar + command.lstrip(),
                                      self.bot,
                                      metadata=metadata)

            # Execute the constructed message
            if inputMessage.Command.lower() in self.bot.moduleHandler.mappedTriggers:
                response = self.bot.moduleHandler.mappedTriggers[inputMessage.Command.lower()].execute(inputMessage)
                """@type : IRCResponse"""
            else:
                return IRCResponse(ResponseType.Say,
                                   u"'{}' is not a recognized command trigger".format(inputMessage.Command),
                                   message.ReplyTo)

            # Push the response onto the stack
            responseStack.append((level, response.Response, start, end))
            # Update the extraVars dict
            extraVars.update(response.ExtraVars)
            metadata = self._mergeDicts(metadata, response.Metadata)

            prevLevel = level

        responseString = self._substituteResponses(subString, responseStack, -1, extraVars, -1)
        responseString = self._unmangleEscapes(responseString)
        return IRCResponse(ResponseType.Say, responseString, message.ReplyTo, extraVars=extraVars, metadata=metadata)

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
    def _substituteResponses(command, responseStack, commandLevel, extraVars, start):
        # Pop responses off the stack and replace the subcommand that generated them
        while len(responseStack) > 0:
            level, responseString, rStart, rEnd = responseStack.pop()
            if level <= commandLevel:
                responseStack.append((level, responseString, rStart, rEnd))
                break
            cStart = rStart - start - 1
            cEnd = rEnd - start
            # Replace the subcommand with its output
            command = command[:cStart] + responseString + command[cEnd:]

        # Replace any extraVars generated by functions
        for var, value in extraVars.iteritems():
            command = re.sub(ur'\$\b{}\b'.format(re.escape(var)), u'{}'.format(value), command)

        return command

    @staticmethod
    def _mangleEscapes(string):
        # Replace escaped left and right braces with something that should never show up in messages/responses
        string = re.sub(ur'(?<!\\)\\\{', u'@LB@', string)
        string = re.sub(ur'(?<!\\)\\\}', u'@RB@', string)
        return string

    @staticmethod
    def _unmangleEscapes(string, unescape=True):
        if unescape:
            # Replace the mangled escaped braces with unescaped braces
            string = string.replace(u'@LB@', u'{')
            string = string.replace(u'@RB@', u'}')
        else:
            # Just unmangle them, ie, keep the escapes
            string = string.replace(u'@LB@', u'\\{')
            string = string.replace(u'@RB@', u'\\}')
        return string

    def _mergeDicts(self, a, b):
        """
        merges b into a and returns the merged result
        NOTE: tuples and arbitrary objects are not handled
        (Heavily) based on http://stackoverflow.com/a/15836901/331047
        @type a: dict
        @type b: dict
        @return: dict
        """
        key = None
        try:
            if a is None or isinstance(a, (basestring, int, long, float)):
                # 'a' is a primitive, or new
                a = b
            elif isinstance(a, list):
                # merge/append lists
                if isinstance(b, list):
                    # merge lists
                    a.extend(b)
                else:
                    # append to list
                    a.append(b)
            elif isinstance(a, dict):
                # merge dicts
                if isinstance(b, dict):
                    for key in b:
                        if key in a:
                            a[key] = self._mergeDicts(a[key], b[key])
                        else:
                            a[key] = b[key]
                else:
                    raise DictMergeError("Cannot merge non-dict '{}' into dict '{}'".format(b, a))
            else:
                raise DictMergeError("NOT IMPLEMENTED '{}' into '{}'".format(b, a))
        except TypeError, e:
            raise DictMergeError("TypeError '{}' in key '{}' when merging '{}' into '{}'".format(e, key, b, a))
        return a
