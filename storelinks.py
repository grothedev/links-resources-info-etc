#!/usr/bin/python3

#an interactive program to add the links from a textfile to the database (json, postgres, sqlite)

import sys
import json
import os


if len(sys.argv) < 2:
    print('provide filename of textfile containing the links')
    sys.exit(0)

f = open(sys.argv[1], 'r')

links = [] #list of links to be written to json file
executable = 'x-www-browser' #set your own if need be. will be passed the url to open with web browser


for l in f: 
    if l in ['\n', '', '\t', ' ']: 
        continue
    print(l)
    #TODO check if the link currently exists in DB
    os.system(f'{executable} {l}')
    print('Enter a label, followed by a semicolon then description, to add to database. otherwise press enter to skip this url. /q to quit')
    action = input('#')
    if action == '':
        continue
    elif action == '/q': #write the entered data, then quit program
        
    else:
        tmp = action.split(';')
        label = tmp[0]
        desc = ''
        if len(tmp) > 1:
            desc = tmp[1]
        links.append({})
        
