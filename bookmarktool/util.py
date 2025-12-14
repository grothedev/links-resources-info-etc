from datetime import datetime
import subprocess
import os
import json

verbose=False
datadir=f'{os.getenv("HOME")}/.local/share/bookmarktool/'
storage_inited = False #has the storage been initialized?

storage = {} #data that the program persists to disk, such as convo history and user preferences. 
  #options: json file, sqlite database


#for now the logging is included in this util module. might break it out later.

def log(msg, label='default'):
    t = tnow()
    d = getLogDir()
    lfpath=f'{d}/{label}.log'
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with open(lfpath, 'a') as lf:
        lf.write(f'{t}: {msg}\n')
        lf.close()
    if verbose: 
        print(f'LOG: {msg}' if label=='default' else f'LOG({label}): {msg}')
    
    
def tnow():
    '''
    return: current time, formatted as %Y%m%d-%H%M%S
    ''' 
    return datetime.now().strftime('%Y%m%d-%H%M%S')

def getLogDir():
  '''
  return: the directory to contain log files for this time period
  '''
  dateStr=datetime.now().strftime('%Y%m%d')
  logdir=f'{datadir}/log/{dateStr}/'
  return logdir


def runcmd(cmdstr,v=False):
    '''
    execute a command using the python subprocess module
    params:
        cmdstr (str) : the command to run
    return: stdout or stderr of command
    '''
    cmdarray = cmdstr.split(' ')
    log(f'runcmd: {cmdstr}')
    if '|' in cmdarray:
        i = cmdarray.index('|')
        proc0 = subprocess.check_output(cmdstr, shell=True)
    proc = subprocess.run(cmdarray, stdout=subprocess.PIPE)
    if proc.returncode == 0:
        res = proc.stdout
        if v:
            log(f'result: {res}')
    else:
        log(f'returncode = {proc.returncode}')
        res = proc.stderr #TODO should also include stdout here? 
    return res
