from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *
from MobroResponses import *

import re

class Instantiate(Function):
	Help = 'Talkwords from your mouth'
	
	def __init__(self):
		try:
			self.responses = MobroResponseDict()

			##################################
			#                                #
			#    ADD RESPONSES HERE, BRO     #
			#                                #
			##################################

			#'''Example'''
			#self.responses.add(MobroResponse(	Name,
			#					Response Message(s),
			#					Regex(es),
			#					ResponseType (default Say),
			#					Enabled (default True),
			#					Seconds Until Response Can Trigger Again (default 300),
			#					All Regexes Must Match (default True)))	
			
			'''Responds to inappropriately combined adjectives'''
			self.responses.add(MobroResponse(	'squishy',
								'GODDAMMIT, GET YOUR HAND OUT OF THERE',
								["([^a-zA-Z]|^)wet (and|&|'?n'?) squishy([^a-zA-Z]|$)","([^a-zA-Z]|^)squishy (and|&|	'?n'?) wet([^a-zA-Z]|$)"],
								ResponseType.Say,
								True,
								300,
								False))
					
			'''Responds to incorrect windmill assumptions'''
			self.responses.add(MobroResponse(	'windmill',
								['WINDMILLS DO NOT WORK THAT WAY!','GOODNIGHT!'],
								['([^a-zA-Z]|^)windmills?([^a-zA-Z]|$)','([^a-zA-Z]|^)cool([^a-zA-Z]|$)']))
			
			'''Responds to Pokemon as Joseph Ducreux'''
			self.responses.add(MobroResponse(	'pokemon',
								'Portable Atrocities! Must be encapsulated en masse!',
								'([^a-zA-Z]|^)pokemon([^a-zA-Z]|$)'))
			
			'''Guards against the Dutch'''
			self.responses.add(MobroResponse(	'dutch',
								'The Dutch, AGAIN!',
								'([^a-zA-Z]|^)dutch([^a-zA-Z]|$)'))

			'''Sensitive to bees'''
			self.responses.add(MobroResponse(	'bees',
								'BEES?! AAAARRGGHGHFLFGFGFLHL',
								'([^a-zA-Z]|^)bee+s?([^a-zA-Z]|$)'))
			
			'''Responds to cheese'''	
			self.responses.add(MobroResponse(	'cheese',
								'loves cheese',
								'([^a-zA-Z]|^)cheese([^a-zA-Z]|$)',
								ResponseType.Do))

			'''Responds to wat'''
			self.responses.add(MobroResponse(	'wat',
								'NaNNaNNaNNaN https://www.destroyallsoftware.com/talks/wat man!',
								'([^a-zA-Z]|^)wat([^a-zA-Z]|$)'))

			#Sorry man, I had to. I HAD to.
			'''Responds to Ponies'''
			self.responses.add(MobroResponse(	'ponies',
								'Ponies Ponies Ponies SWAG! https://www.youtube.com/watch?v=hx30VHwKa0Q',
								'([^a-zA-Z]|^)ponies([^a-zA-Z]|$)'))


			#This one needs to mess with the object to work right.
			'''Responds to DuctTape being a dick in minecraft'''
			def ducktapeMatch(message):
				match = re.search('([^a-zA-Z]|^)minecraft([^a-zA-Z]|$)', message, re.IGNORECASE)
				self.ductMatch = re.search('([^a-zA-Z]|^)(?P<duc>duc[kt]tape)([^a-zA-Z]|$)',message,re.IGNORECASE)
				return match and self.ductMatch

			def ducktapeTalkwords(chatMessage):
				return [IRCResponse(ResponseType.Say,'Just saying, %s is a dick in Minecraft' % self.ductMatch.group('duc'),chatMessage.ReplyTo)]

			ducktape = MobroResponse('ducktape','','')
			ducktape.match = ducktapeMatch
			ducktape.talkwords = ducktapeTalkwords
			self.responses.add(ducktape)

			##################################
			#                                #
			#   OK I'VE GOT THIS NOW, BRO    #
			#                                #
			##################################
		except Exception, e:
			print e



	def GetResponse(self, message):
		if message.Type != 'PRIVMSG':
			return
		
		if message.Command is not '':
			match = re.search('^responses?$', message.Command, re.IGNORECASE)
			if not match:
				return
			enableds = []
			for param in message.ParameterList:
				enableds.append(self.responses.toggle(param,message))
			return enableds
		else:
			triggers = []
			for response in self.responses.dict:
				trig = self.responses.dict[response].trigger(message)
				if isinstance(trig,str):
					trig = [trig]
				try:
					triggers.extend(trig)
				except:
					triggers = triggers
			return triggers
