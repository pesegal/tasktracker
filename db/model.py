"""
    This file contains the code that models the database layout. Test database setup will be done in SQLite
"""

import sqlite3


db = sqlite3.connect('tt_dev')

cursor = db.cursor()



