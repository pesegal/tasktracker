"""
    This module contains all the logic to communicate data with the database.
"""

import os
import os.path
import shutil
import sqlite3
from datetime import datetime, timezone
from threading import Thread
from queue import Queue
from kivy.clock import Clock
from functools import partial


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class SqlTask:
    def __init__(self, statement, args=None, function=None, callback=None):
        self.function = function  # The function to call when returning sql data. E.G. 'fetchone()
        self.statement = statement
        self.args = args
        self.callback = callback

    def __str__(self):
        return """SqlTask Object: -----------------------------------------------------------
                  Statement: %s
                  Arguments: %s
                  Function:  %s
                  Callback:  %s""" % (self.statement, self.args, self.function, self.callback)


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

        self.action_queue = Queue()
        self.db_thread = Thread(target=self._database_loop, args=(self.path,))
        self.db_thread.start()

    def _database_loop(self, path):
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')

        while True:
            item = self.action_queue.get()
            print(item)
            if item.statement == 'shutdown':
                break

            if item.args:
                cursor.execute(item.statement, item.args)
            else:
                cursor.execute(item.statement)

            if item.function and item.callback:
                result = getattr(cursor, item.function)()
                Clock.schedule_once(partial(item.callback, result))

            if self.action_queue.empty() or item.function == 'force_commit':
                connection.commit()

            self.action_queue.task_done()

        print('Thread Shutting Down', self.db_thread.ident)
        connection.commit()
        connection.close()
        if item.callback and item.statement == 'shutdown':  # If shutdown callback passed.
            Clock.schedule_once(partial(item.callback, item.args))

    def backup_database(self, controller, dst_path):
        """ This function creates a backup of the sqlite database by copying the
            dbfile. This shuts down the db thread and restarts the db thread after copying
            to avoid file corruption
            :param dst_path - full path and filename for the db backup.
            :return true if the

        """
        if self.db_thread.is_alive():
            self.action_queue.put(
                SqlTask(statement='shutdown',
                        callback=self._database_backup,
                        args=(controller, dst_path)
                        )
            )

    def _database_backup(self, arguments, dt):
        """ Callback to do the database copy once the thread has shutdown """

        # TODO handle errors

        print("database._database_backup", arguments)
        obj = arguments[0]
        path = arguments[1]
        try:
            shutil.copyfile(self.path, path)

        except OSError as os_err:
            # Write permissions don't exist.
            print('OS ERROR')

        except shutil.SameFileError as sf_err:
            # When self.path = dst_path
            print(SameFile_error)

        finally:
            self.thread_startup()

    def thread_status(self):
        print("Thread is alive: ", self.db_thread.is_alive(), self.db_thread.ident)

    def thread_startup(self):
        """ if the thread is dead """
        if not self.db_thread.is_alive():
            self.db_thread = Thread(target=self._database_loop, args=(self.path,))
            self.db_thread.start()
            print("New thread created ", self.db_thread.ident)

    def thread_shutdown(self):
        self.action_queue.put(SqlTask('shutdown'))

    def load_all_tasks(self, callback):
        self.action_queue.put(
            SqlTask("SELECT * FROM tasks ORDER BY list_id, list_pos ASC;",
                    function='fetchall',
                    callback=callback)
        )

    def load_all_projects(self, callback):
        self.action_queue.put(
            SqlTask('SELECT * FROM projects;',
                    function='fetchall',
                    callback=callback)
            )
        self.action_queue.join()

    def update_task_list_index(self, index, task_id):
        self.action_queue.put(
            SqlTask('UPDATE tasks SET list_pos = ? WHERE id = ?;',
                    args=(index, task_id))
        )
        # Uncomment this to see the advantage of multi-threading!

    def task_switch(self, task_id, list_id):
        list_id += 1
        self.action_queue.put(
            SqlTask('INSERT INTO column_history(creation_date, task_id, column_id) VALUES (?,?,?);',
                    args=(datetime.now(timezone.utc), task_id, list_id))
        )
        self.action_queue.put(
            SqlTask('UPDATE tasks SET list_id = ? WHERE id = ?;', args=(list_id, task_id))
        )

    def load_task_data(self, task_id, callback):
        self.action_queue.put(
            SqlTask('SELECT * FROM tasks WHERE id = ?;',
                    args=(task_id,),
                    function='fetchone',
                    callback=callback)
        )

    def add_new_task(self, task_name, task_notes, list_id, list_pos, project_id, callback):
        now = datetime.now(timezone.utc)
        list_id += 1

        def _return_last_id(row_id, td):
            self.action_queue.put(
                SqlTask('INSERT INTO column_history(creation_date, task_id, column_id) VALUES (?,?,?);',
                        args=(now, row_id[0], list_id))
            )
            callback(row_id[0])

        self.action_queue.put(
            SqlTask('INSERT INTO tasks(creation_date, project_id, list_id, list_pos, name, notes) VALUES (?,?,?,?,?,?);',
                    args=(now, project_id, list_id, list_pos, task_name, task_notes)
                    )
        )
        self.action_queue.put(
            SqlTask('SELECT max(id) FROM tasks;',
                    function='fetchone',
                    callback=_return_last_id
            )
        )

    def update_task(self, task_id, name, notes, project_id):
        self.action_queue.put(
            SqlTask('UPDATE tasks SET name = ?, notes = ?, project_id = ? WHERE id = ?;',
                    args=(name, notes, project_id, task_id))
        )

    def delete_task(self, task_id, list_id):
        now = datetime.now(timezone.utc)
        list_id += 1
        self.action_queue.put(
            SqlTask('UPDATE tasks SET deletion_date=?, list_id=? WHERE id=?;',
                    args=(now, list_id, task_id))
        )

    def write_task_action(self, action):
        self.action_queue.put(
            SqlTask("""INSERT INTO task_actions(task_id, creation_date, finish_date, action_id, project_id)
                    VALUES (?,?,?,?,?);""",
                    args=(action.task_id, action.start_time, action.finish_time, action.type, action.project_id))
        )

    def new_project(self, name, color, color_name, callback):
        self.action_queue.put(
            SqlTask('INSERT INTO projects(creation_date, name, color, color_name) VALUES (?,?,?,?);',
                    args=(datetime.now(timezone.utc), name, color, color_name))
        )
        self.action_queue.put(
            SqlTask('SELECT max(id) FROM projects;',
                    function='fetchone',
                    callback=callback)
        )

    def update_project(self, project):
        self.action_queue.put(
            SqlTask('UPDATE projects SET name = ?, color = ?, color_name = ? WHERE id = ?;',
                    args=(project.name, project.color, project.color_name, project.db_id))
        )

    def load_task_actions(self, start_time, end_time, callback):
        self.action_queue.put(
            SqlTask('SELECT * FROM task_actions WHERE creation_date >= ? AND finish_date <= ?;',
                    args=(start_time, end_time),
                    function='fetchall',
                    callback=callback)
        )

    def get_action_type(self, type_id, callback):
        self.action_queue.put(
            SqlTask('SELECT action_description FROM action_type WHERE id = ?;',
                    args=(type_id,),
                    function='fetchone',
                    callback=callback)
        )

    def delete_project(self, project):
        pass

DB = Database(os.path.join(__location__, 'tt_dev.db'))
