#!/usr/bin/python3

import argparse
import sys

#this is the CLI tool for managing the links database
"""
use examples:
    - `links` [url] : add a url
    - `links` a[dd] [url] : add a url
    - `links` d[elete] [url] : remove a url
    - any of the following options can be added to any of the above commands
    - `-t` : attach a tag or a list of tags 
    - 
    
behavioral description:
    - after a link is submitted, the program will then prompt the user if they want populate any unset fields
    - after some time with no user input, the program will exit, saving the link
    - 

operations:
    - add
    - delete
        - local only, or also remote, 
        - option to select by ID
    - update/edit
        - edit field(s) of an existing link
    - analyze
    - synchronize, 
    - 

"""

def parseArgs():
    parser = argparse.ArgumentParser(description='the program does a thing')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose')
    subparsers = parser.add_subparsers(dest='command', help='the operation to perform')

    parser_add = subparsers.add_parser('add', help='add a link to the database', aliases='a')
    parser_add.add_argument('url', help='the url')
    #parser_add.add_argument('--tag', '-t', help='tags to associate with the url')
    #parser_add.add_argument('--description', '--desc', '-d', help='description of the link')

    parser_del = subparsers.add_parser('delete', aliases=['del', 'd', 'de'], help='delete a link')
    #parser_del.add_argument('url', help='the url to delete') #will search for link(s) then ask user to confirm
    #parser_del.add_argument('--id', '-i', help='select by id')

    parser_edit = subparsers.add_parser('edit', aliases=['e'], help='edit an existing link')
    #parser_edit

    parser_analyze = subparsers.add_parser('analyze', aliases=['an'], help='analyze state of link databases')

    parser_search = subparsers.add_parser('search', aliases=['s', 'se', 'srch', 'sch', 'sr'], help='search for a link')
    parser_search.add_argument('query', help='the search query')


    parser.add_argument('--tag', '-t', help='tags to associate with the url')
    parser.add_argument('--description', '--desc', '-d', help='description of the link')
    parser.add_argument('--id', '-i', help='select by id')
    

    
    args = parser.parse_args()
    return args

def main():
    args = parseArgs()
    
    print(args)
    



if __name__ == '__main__':
    main()
