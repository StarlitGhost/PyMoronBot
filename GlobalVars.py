import os

functions = {}
CurrentNick = 'MoronBot'
server = 'irc.desertbus.org'
channels = ['#unmoderated', '#survivors', '#help', '#desertbus']

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
logPath = os.path.join(dname, 'logs')

