import os, sys
from glob import glob
import GlobalVars

def LoadCommand(name, loadAs=''):

    name = name.lower()

    cmdList = GetCommandDirList()
    cmdListCaseMap = {key.lower(): key for key in cmdList}

    if name not in cmdListCaseMap:
        return False

    alreadyExisted = False

    src = __import__('Commands.' + cmdListCaseMap[name], globals(), locals(), [])
    if loadAs != '':
        name = loadAs.lower()
    if name in GlobalVars.commandCaseMapping:
        alreadyExisted = True
        properName = GlobalVars.commandCaseMapping[name]
        del sys.modules['Commands.{0}'.format(properName)]
        for f in glob ('Commands/{0}.pyc'.format(properName)):
            os.remove(f)
        
    reload(src)

    components = cmdListCaseMap[name].split('.')
    for comp in components[:1]:
        src = getattr(src, comp)
    
    if alreadyExisted:
        print '-- {0} reloaded'.format(src.__name__)
    else:
        print '-- {0} loaded'.format(src.__name__)
    
    command = src.Command()
    
    GlobalVars.commands.update({cmdListCaseMap[name]:command})
    GlobalVars.commandCaseMapping.update({name : cmdListCaseMap[name]})

    return True

def UnloadCommand(name):

    if name.lower() in GlobalVars.commandCaseMapping.keys():
        del GlobalVars.commands[GlobalVars.commandCaseMapping[name]]
        del GlobalVars.commandCaseMapping[name.lower()]
    else:
        return False

    return True

def AutoLoadCommands():

    for command in GetCommandDirList():
        try:
            LoadCommand(command)
        except Exception, x:
            print x.args

def GetCommandDirList():

    root = os.path.join('.', 'Commands')

    for item in os.listdir(root):
        if not os.path.isfile(os.path.join(root, item)):
            continue
        if not item.endswith('.py'):
            continue
        if item.startswith('__init__'):
            continue

        yield item[:-3]