from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function

import re, math

class Instantiate(Function):
    Help = 'dbcalc (hours <hours> / money <money>) - tells you how much money is required for a given number of hours, or how many hours will be bussed for a given amount of money'

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return

        match = re.search('^dbcalc$', message.Command, re.IGNORECASE)
        if not match:
            return

        if len(message.ParameterList) < 2:
            return IRCResponse(ResponseType.Say, self.Help, message.ReplyTo)

        if message.ParameterList[0].lower() == 'hours':
            return IRCResponse(ResponseType.Say, Hours(message.ParameterList[1]), message.ReplyTo)
        elif message.ParameterList[0].lower() == 'money':
            return IRCResponse(ResponseType.Say, Money(message.ParameterList[1]), message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say, self.Help, message.ReplyTo)

    def Hours(self, hours):

        hours = 0.0
        money = 0.0

        try:
            hours = float(message.ParameterList[0])
        except ValueError:
            return "Sorry, I don't recognize '{0}' as a number".format(message.ParameterList[0])

        try:
            money = (1-(1.07**hours))/(-0.07)
        except OverflowError:
            return "The amount of money you would need for that many hours is higher than I can calculate!"

        return "For {0:,} hour(s), the team needs a total of ${1:,.2f}".format(hours, money)

    def Money(self, money):

        hours = 0.0
        money = 0.0

        try:
            money = float(message.ParameterList[0])
        except ValueError:
            return "Sorry, I don't recognize '{0}' as a number".format(message.ParameterList[0])

        try:
            hours = math.log((7*money)/100 + 1)/math.log(1.07)
        except OverflowError:
            return "???"

        return "With ${0:,.2f}, the team will bus for {1:,.2f} hour(s)".format(money, hours)
