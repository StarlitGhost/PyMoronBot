import os

functions = {}

CurrentNick = 'PyMoronBot'
server = 'irc.desertbus.org'#'irc.applejack.me'#'irc.desertbus.org'
port = 6667
channels = ['#survivors']#, '#desertbus', '#unmoderated', '#help', '#games']
admins = ['Tyranic-Moron', 'T-M|Work', 'Tyranic_Moron', 'T-M|Asleep', 'LordCustardSmingleigh', 'HappyHAL9k', 'XelaReko', 'XelaReco', 'dave_random', 'ElementalAlchemist', 'Homoglyph']

finger = 'GET YOUR FINGER OUT OF THERE'
version = '0.0.1'
source = 'https://github.com/MatthewCox/PyMoronBot/'

CommandChar = '\\'

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
logPath = os.path.join(dname, 'logs')

