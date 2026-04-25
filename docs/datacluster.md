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
            2. for each file, check if already exists in database (via md5 hash), if not, check via filename. 
                2a. if file with same hash exists, let the user know and proceed with normal metadata modification
                2b. if filename already exists but the hash is different, ask the user what to do, telling them the file, hashes, filesizes, and modified/creation times of the files.
                2c. if neither hash nor same-named file exist in the DB, proceed with adding the file to the DB
            3. ask the user to provide the appropriate metadata for the file (title, author, description, categories). category can already be filled in if the user specified that this folder is for some category.
            4. 

                

#### Systems, Modules, Considerations 
    * user can interface with the system via command line, website, or REST API
    * there needs to be a process by which data is kept synchonized among the datastorages. 
        * multiple mirrored postgres DBs, multiple sqlite DB files, multiple JSON files, different endpoints
        * remote DBs could be interfaced with via RPC API. look into existing distribute data management solutions. (consul? bittorrent? )
        * how to handle remote sqlite and json files? ssh? again research existing solutions. 
    * how to handle multiple users adding resources? we should allow for multiple users to add resources. so we'll have to keep track of who uploaded/added what. 
    * for now we will store URLs as 1 string, but in the future it might prove useful to separate out into domain, path, query args, etc. 
    * there is an API for client CRUD applications //TODO more detail 
    * the program is "local first", so that it can be used to update the user's local DB if his primary service node is unreachable

#### Database Schema
    (assume default fields id, created & modified timestamp)
    * URL
        *title:string
        *value:string
        *description:string #nullable
    * Tag #or Category
        *label:string
        *description:string #nullable
        *refs:int #how many objects have this tag associated with them
    * File
        *filename:string
        *path:string
        *title:string
        *description:string #nullable
        *md5:string
        *author:string #nullable
    * Pivot Tables
        * tag to url
        * tag to file

#### User Experience
    * option to use a website, CLI tool, or mobile app
    * //TODO continue here


------ below this line is early rough draft which i am consolidating and clarifying and putting into the official spec ------------------

- in the future, will tie other datatypes in as well



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

