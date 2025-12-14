#!/usr/bin/python3

import argparse
import sys
import stor

"""
this is the client for the bookmark tool.
it provides functions to access the bookmark datastore, whether it be local or remote, json file, sqlite, database, or web service.

operations:
    - add
    - delete
        - local only, or also remote, 
        - option to select by ID
    - update/edit
        - edit field(s) of an existing link
    - analyze
    - synchronize, 
    - use REPL

"""

bookmarks = []

def init():
    #prepare auth 
    #establish connection to storage
    stor.init()


def add(url, title, tags, description):
    link = dict()
    #validate data
    #check if already exists (use fuzzy compare. notify user of inexact matches)
    #write to local db
    #write to local json file
    #update log
    #notify that new resource has been added (so that the sync daemon can handle)
    #???

def deleteByID(id):
    return

def deleteByURL(url):
    return
        