"""
    This file contains the code that models the database layout. Test database setup will be done in SQLite
"""

import os
import sqlite3
from datetime import datetime
from sqlite3 import OperationalError

RESET_DATABASE = True

print(sqlite3.sqlite_version)

if RESET_DATABASE:
    os.remove('tt_dev.DB')


def execute_scripts_from_file(filename):
    fd = open(filename, 'r')
    sql_file = fd.read()
    fd.close()

    sql_commands = sql_file.split(';')

    for command in sql_commands:
        try:
            cursor.execute(command)
        except OperationalError as msg:
            print('Command Skipped: ', msg)

db = sqlite3.connect('tt_dev.DB')
cursor = db.cursor()

execute_scripts_from_file('tt_schema.sql')
# Insert Defaults

columns = (
    'Today',
    'Tomorrow',
    'Future',
    'Done'
)

for data in columns:
    cursor.execute("INSERT INTO columns(creation_date, name) VALUES (?,?)", (datetime.now(), data))

action_types = (
    'unknown',
    'Pomodoro',
    'Pause',
    'Short Break',
    'Long Break',
    'Stopwatch Start',
    'Stopwatch Stop'
)

for data in action_types:
    cursor.execute("INSERT INTO action_type(creation_date, action_description) VALUES (?,?)", (datetime.now(), data))

cursor.execute("INSERT INTO projects(id, creation_date, name) VALUES (?,?,?)", (0, datetime.now(), 'No Project'))

db.commit()
db.close()
