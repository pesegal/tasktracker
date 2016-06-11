"""
    This module contains all the logic to communicate data with the database.
"""

import os
import os.path
import sqlite3
from datetime import datetime


class Database:
    """
        Database class handles all read/write connections with the database for TaskTracker App.
        this will allow for flexibility in the future when accessing multiple databases.
    """
    def __init__(self, path):
        self.path = path
        self.connection = None
        self.cursor = None
        if not os.path.isfile(self.path):
            raise FileExistsError("File not found.", self.path)
        elif not os.access(self.path, os.R_OK):
            raise PermissionError("File not readable.", self.path)

        self.open_connection()

    def open_connection(self):
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()

    def load_all_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        return self.cursor.fetchall()

    def add_new_task(self, task_name, task_notes, list_id, project_id=0):
        now = datetime.now()
        list_id += 1
        # Insert the task record
        self.cursor.execute('INSERT INTO tasks(creation_date, project_id, list_id, name, notes) VALUES (?,?,?,?,?)',
                            (now, project_id, list_id, task_name, task_notes))
        task_id = self.cursor.lastrowid
        # Insert the column history record
        self.cursor.execute('INSERT INTO column_history(creation_date, task_id, column_id) VALUES (?,?,?)',
                            (now, task_id, list_id))

        self.connection.commit()
        return task_id


    def update_task(self, task):
        pass

    def task_switch(self, task):
        pass

    def task_action(self, task):
        pass

    def task_archive(self, task):
        pass

    def new_project(self, project):
        pass

    def delete_project(self, project):
        pass

    def close_connection(self):
        self.connection.close()

db = Database('./db/tt_dev.db')
