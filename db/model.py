"""
    This file contains the code that models the database layout. Test database setup will be done in SQLite
"""

import os
import sqlite3
from sqlite3 import OperationalError

RESET_DATABASE = True

if RESET_DATABASE:
    os.remove('tt_dev.db')


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


db = sqlite3.connect('tt_dev.db')
cursor = db.cursor()

execute_scripts_from_file('tt_schema.sql')


db.commit()

db.close()
