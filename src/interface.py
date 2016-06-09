"""
    This module contains all the logic to communicate data with the database.
"""

import os
import os.path
import sqlite3


class Database:
    """
        Database class handles all read/write connections with the database for TaskTracker App.
        this will allow for flexibility in the future when accessing multiple databases.
    """
    def __init__(self, path):

        self.path = path
        if not os.path.isfile(self.path):
            raise FileExistsError("File not found.", self.path)
        elif not os.access(self.path, os.R_OK):
            raise PermissionError("File not readable.", self.path)

        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()

    def load_all_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        return self.cursor.fetchall()

    def add_new_task(self, task):


    #TODO: Update a task to the database

    #TODO: Track Task Switching

    #TODO: Track Task Actions

    #TODO: Task Archive

    #TODO: Stats Stuff

    #TODO: Project Creation

a = connect('../db/tt_dev.db')
