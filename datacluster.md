# Overview
this document shall descibe a new application that i am making called "The DataCluster". 
it will help the user to keep track of URLs and important files by keeping them stored, with metadata, in a local database, json file, and/or any other place that is configured. there will be a CLI tool to use it and a nice web interface. it will also check for duplicate files and keep resources in sync when it is updated from just one location. it will help the user keep their stuff organized by noticing if some entry doesn't have some metadata field like author or description for example. it can be configured to watch some directories for changes and automatically add new files to the store, notifying the user somehow if any information needs be updated. 
TL;DR it is an advanced bookmark manager that also stores metadata about files. 

## Background:
For context, here is my usecase: I have a collection of URLs to useful websites and online resources, a bunch of PDFs of books, and a bunch of PDFs of research papers. These have gotten a little unorganized, with the PDFs being somewhat scattered between different devices and the links not having their metadata updated because of my laziness. At one point I tried to separate out links having to do with education into a different file, and i think that just made things more confusing. So I have a text file that contains a bunch of URLs, some with metadata and some without.

## Proposed Architecture
- runs as a systemd service (but you can run it standalone if needed)
#### setup stage
    1. to set up the application, the user must first set up authentication. this could just be the local user account. though it might be good to allow an additional layer of security, especially if the service is being provided to multiple users. 
        - TODO detail user account set up
    2. Database or other persistant data-storage configuration
        - local postgresql database running on same machine: set tables, user, password. requires that the user has a user account on the postgresql db. will run a query to create the needed tables. 
        - local sqlite database: user sets path. run query to create needed tables.
        - local json file: user sets path. 
        - remote: //TODO 
    3. the user can then populate the store with bulk resources from a text file and from some folders on the filesystem 
        - URLs from text file: 
            1. scan through the text file, grabbing anything that's a valid URL, ignoring other text
            2. for each URL, check to see if it already exists in any of the datastorages. query the URL to verify it is reachable and to grab some basic default metadata (title, short description, category), then prompt the user, asking if they want to keep the URL or edit any of the default metadata. notify them if it's unreachable and add it to a list of unreachable URLs (or just use a database field to indicate as such). 
            3. if user accepts URL, add it to all of the configured datastorages (or maybe just the primary one, and let the data-sync process automatically handle redundancy. actually this concern doesn't matter at this level of procedural description because we're just calling upon the "persistant-data-storage module of the software)
            4. notify user when the operation is complete and everything is written to the database. provide the user with a cleaned up and nicely-formatted version a the file, showing each URL with its metadata and the dead URLs listed at the bottom. 
        - Files in folders:
            1. the user has the option to associate each folder with a category. scan through each folder for valid files (known document formats like pdf, txt, docx, ppt, md, tex, html. maybe it would be easier to instead blacklist binary files, hidden files, anything obviously not a "document-for-human" file). 
            2. for each file, check if already exists in database (via md5 hash) 
#### Systems, Modules, Considerations 
    * user can interface with the system via command line, website, or REST API
    * there needs to be a process by which data is kept synchonized among the datastorages. 
    *   
#### Database Schema
#### User Experience


- there can be some number of duplicated postgres DBs
- there are mirrors which store the resource identifiers via sqlite and json
- there is an API for client CRUD applications
    - the API webserver interfaces with any or all of postgres, sqlite, json file. 
    - an API webserver doesn't have to know about the other APIs. however, it can so that it can notify others of requests or any data modification. the other will compare hash or ID of request to check if they also got it and respond accordingly. 
    - use soft delete before actual delete after long time of no access
    - the API webserve is managed by a systemd service. it might be beneficial to have it be able to do some other things in addition to simply starting/restarting the webserver
- there is a website, CLI tool, and mobile app
- in the future, will tie other datatypes in as well
    - 



i started converting these to json using a python script, and from that made a json file, to associate meta data with them. 



example usage:
    - core module: probably python. 
    -
    - CLI tool:
        - uses the core module
        -
        - `links add [url]`
        - `links add [url] [title]` or `links add [title] [url]`. the program will be smart enough to know what you meant. 
        - `options: -t [tag]; -d [description]; `
        - adds link to local store first of all, which is either a sqlite db or json file or both. then makes a request for each remote server to add it to that server. 
        - should probably be a REPL mode
        - one goal is to very informational to the user. when the program is ran, it finds the primary database file (always a local sqlite or json file) and validates it, then reports the status. 
    
    - website: consolidate the 2 existing UIs on the website: file browser and link list. 
        - user can configure a set of remote datasources to use (with priority maybe). probably don't use local storage. could use a server runningn on localhost
        -

