import os, sys
from glob import glob
import GlobalVars

def LoadFunction(name, loadAs=''):

    name = name.lower()

    funcList = GetFunctionDirList()
    funcListCaseMap = {key.lower(): key for key in funcList}

    if name not in funcListCaseMap:
        return False

    alreadyExisted = False

    src = __import__('Functions.' + funcListCaseMap[name], globals(), locals(), [])
    if loadAs != '':
        name = loadAs.lower()
    if name in GlobalVars.functionCaseMapping:
        alreadyExisted = True
        properName = GlobalVars.functionCaseMapping[name]
        del sys.modules['Functions.{0}'.format(properName)]
        for f in glob ('Functions/{0}.pyc'.format(properName)):
            os.remove(f)
        
    reload(src)

    components = funcListCaseMap[name].split('.')
    for comp in components[:1]:
        src = getattr(src, comp)
    
    if alreadyExisted:
        print '-- {0} reloaded'.format(src.__name__)
    else:
        print '-- {0} loaded'.format(src.__name__)
    
    func = src.Instantiate()
    
    GlobalVars.functions.update({funcListCaseMap[name]:func})
    GlobalVars.functionCaseMapping.update({name : funcListCaseMap[name]})

    return True

def UnloadFunction(name):

    if name.lower() in GlobalVars.functionCaseMapping.keys():
        del GlobalVars.functions[GlobalVars.functionCaseMapping[name]]
        del GlobalVars.functionCaseMapping[name.lower()]
    else:
        return False

    return True

def AutoLoadFunctions():

    for func in GetFunctionDirList():
        try:
            LoadFunction(func)
        except Exception, x:
            print x.args

def GetFunctionDirList():

    root = os.path.join('.', 'Functions')

    for item in os.listdir(root):
        if not os.path.isfile(os.path.join(root, item)):
            continue
        if not item.endswith('.py'):
            continue
        if item.startswith('__init__'):
            continue

        yield item[:-3]