"""
    This module contains all the logic to communicate data with the database.
"""

import os
import os.path
import sqlite3
from datetime import datetime
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


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
        self.cursor.execute('PRAGMA foreign_keys = ON')

    def open_connection(self):
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()

    def load_all_tasks(self):
        self.cursor.execute("SELECT * FROM tasks ORDER BY list_id, list_pos ASC;")
        return self.cursor.fetchall()

    def load_task_data(self, task_id):
        self.cursor.execute('SELECT * FROM tasks WHERE id = ?;', (task_id,))
        return self.cursor.fetchone()

    def add_new_task(self, task_name, task_notes, list_id, list_pos, project_id=0):
        now = datetime.now()
        list_id += 1
        # Insert the task record
        self.cursor.execute('INSERT INTO tasks(creation_date, project_id, list_id, list_pos, name, notes)' +
                            ' VALUES (?,?,?,?,?,?);', (now, project_id, list_id, list_pos, task_name, task_notes))
        task_id = self.cursor.lastrowid
        # Insert the column history record
        self.cursor.execute('INSERT INTO column_history(creation_date, task_id, column_id) VALUES (?,?,?);',
                            (now, task_id, list_id))

        self.connection.commit()
        return task_id

    def update_task_list_index(self, index, task_id):
        self.cursor.execute('UPDATE tasks SET list_pos = ? WHERE id = ?', (index, task_id))
        self.connection.commit()

    def update_task(self, task_id, name, notes, project_id):
        # TODO: Update to allow tasks to be deleted as well.
        print(name, notes, project_id, task_id)
        self.cursor.execute('UPDATE tasks SET name = ?, notes = ?, project_id = ? WHERE id = ?;',
                            (name, notes, project_id, task_id))
        self.connection.commit()

    def task_switch(self, task_id, list_id):
        list_id += 1
        # TODO: Figure out why task are writing index changes to task list change history.
        self.cursor.execute('INSERT INTO column_history(creation_date, task_id, column_id) VALUES (?,?,?);',
                            (datetime.now(), task_id, list_id))
        self.cursor.execute('UPDATE tasks SET list_id = ? WHERE id = ?;', (list_id, task_id))
        self.connection.commit()

    def task_action(self, task):
        pass

    def task_archive(self, task):
        pass

    def load_all_projects(self):
        self.cursor.execute('SELECT * FROM projects;')
        return self.cursor.fetchall()

    def new_project(self, name, color, color_name):
        self.cursor.execute('INSERT INTO projects(creation_date, name, color, color_name) VALUES (?,?,?,?);',
                            (datetime.now(), name, color, color_name))
        project_id = self.cursor.lastrowid
        self.connection.commit()
        return project_id

    def update_project(self, project):
        self.cursor.execute('UPDATE projects SET name = ?, color = ?, color_name = ? WHERE id = ?;',
                            (project.name, project.color, project.color_name, project.db_id))
        self.connection.commit()

    def delete_project(self, project):
        pass

    def close_connection(self):
        self.connection.close()


db = Database(os.path.join(__location__, 'tt_dev.db'))
