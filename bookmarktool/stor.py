import os
import json
from util import *

verbose=False
storfile=datadir+"/stor.json"
storage_inited = False #has the storage been initialized?

storage = {} #data that the program persists to disk, such as convo history and user preferences. 
  #options: json file, sqlite database
  # i think storing everything in a json file is fine for something small scale. but will have to update to use sqlite. 


def init():
  global storage
  global storage_inited
  if storage_inited:
    log('storage already initialized')
    return True
  gotStorageFile = False
  if not os.path.isfile(f'{datadir}/stor.json'):
    fStor = open(f'{datadir}/stor.json','w')
    fStor.write(json.dumps(storage))
    gotStorageFile = True
    fStor.close()
    storage = {}
  else:
    fStor = open(f'{datadir}/stor.json','r')
    fStorBak = open(f'{datadir}/stor.bak{tnow()}.json','w')
    storText = fStor.read()
    fStorBak.write(storText)
    storage = json.loads(storText)
    gotStorageFile = True
    fStor.close()
    fStorBak.close()
    
  if gotStorageFile:
    storage_inited = True
    log('loaded storage')
    return True
  else:
    log('failed to load storage')
    return False

def get(k):
  if k in storage:
    return storage[k]
  else:
    log(f'error: storage does not contain {k}')

def put(k, v):
  storage[k] = v
  write()

def write(data = None):
  fStor = open(f'{datadir}/stor.json','w')
  if fStor:
    fStor.write(json.dumps(storage if data == None else data))
  else:
    log('error: could not open storage file')
  
