from fnmatch import fnmatch
from functools import wraps, partial

from pymoronbot.moduleinterface import BotModule
from pymoronbot.response import IRCResponse, ResponseType


def admin(func=None, msg=''):
    if callable(func):
        @wraps(func)
        def wrapped_func(inst, message):
            print(func)
            print(msg)

            if not inst.checkPermissions(message):
                if msg:
                    return IRCResponse(ResponseType.Say, msg, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say,
                                       "Only my admins may use {!r}".format(message.Command),
                                       message.ReplyTo)
            return func(inst, message)

        return wrapped_func
    else:
        return partial(admin, msg=func)  # this seems wrong, should be msg=msg


def ignore(command):
    @wraps(command)
    def wrapped(inst, message):
        if not inst.checkIgnoreList(message):
            return
        return command(inst, message)

    return wrapped


class BotCommand(BotModule):
    runInThread = False

    def triggers(self):
        return []

    def actions(self):
        return super(BotCommand, self) + [('botmessage', 1, self.handleCommand)]

    def onLoad(self):
        self.triggerHelp = {}

    def help(self, arg):
        if arg.lower() in self.triggerHelp:
            return self.triggerHelp[arg]

    def checkPermissions(self, message):
        """
        @type message: IRCMessage
        @rtype Boolean
        """
        for owner in self.bot.config.getWithDefault('owners', []):
            if fnmatch(message.User.String, owner):
                return True
        for admin in self.bot.config.getWithDefault('admins', []):
            if fnmatch(message.User.String, admin):
                return True
        return False

    def checkIgnoreList(self, message):
        """
        @type message: IRCMessage
        @rtype Boolean
        """
        for ignore in self.bot.config.getWithDefault('ignored', []):
            if fnmatch(message.User.String, ignore):
                return True
        return False

    def handleCommand(self, message):
        if not self.shouldExecute(message):
            return

        try:
            self.execute(message)
        except Exception as e:
            error = u"Python execution error while running command {!r}: {}: {}".format(message.Command,
                                                                                        type(e).__name__,
                                                                                        e.message)
            self.bot.moduleHandler.sendPRIVMSG(error, message.ReplyTo)
            self.bot.log.failure(error)

    def shouldExecute(self, message):
        """
        @type message: IRCMessage
        @rtype Boolean
        """
        if message.Command.lower() not in [t.lower() for t in self.triggers()]:
            return False

        return True

    def execute(self, message):
        """
        @type message: IRCMessage
        @rtype IRCResponse | list[IRCResponse]
        """
        return IRCResponse(ResponseType.Say, '<command not yet implemented>', message.ReplyTo)
