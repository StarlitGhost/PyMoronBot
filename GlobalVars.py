import os

functions = {}

CurrentNick = 'PyMoronBot'
server = 'irc.desertbus.org'
port = 6667
channels = ['#unmoderated', '#survivors', '#help', '#desertbus']
admins = ['Tyranic-Moron', 'T-M|Work', 'Tyranic_Moron', 'T-M|Asleep', 'LordCustardSmingleigh']

finger = 'GET YOUR FINGER OUT OF THERE'
version = '0.0.1'
source = 'https://github.com/MatthewCox/PyMoronBot/'

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
logPath = os.path.join(dname, 'logs')

