import sqlite3
from datetime import datetime

class DBM:
    db_path = ''
    db_type = 'sqlite' #pg | mysql | sqlite | mongo | dyn
    db_table = 'default'
    conn = None #the database connection
    _ = '' #the database cursor

    def __init__(self, db_path='database.sqlite', db_type='sqlite'):
        self.db_path = db_path
        self.db_type = db_type

    def initDB(self):
        if db_type == 'sqlite':
            self.conn = sqlite3.connect(self.db_path)
            self._ = self.conn.cursor()
            #check if db already inititialized or we need to set up the schema

            self._.execute()
        elif db_type == 'pg':
            return
        elif db_type == 'mysql':
            return
        elif db_type == 'mongo':
            return
        
    def insert(self, table, fields=[], values=[]):
        if len(fields) == 0 or len(values) == 0: return
        fields.append('time_created')
        values.append(datetime.now().timestamp())

        try:
            self._.execute(f'INSERT INTO {table} ({','.join(fields)}) VALUES ({','.join(values)})')
            self.conn.commit()
        except sqlite3.Error as err:
            print(err)

    def update(self, table, fields=[], values=[]):
        if len(fields) == 0 or len(values) == 0: return

        try:
            self._.execute(f'REPLACE INTO {table} ({','.join(fields)}) VALUES ({','.join(values)})')
            self.conn.commit()
        except sqlite3.Error as err:
            print(err)

    