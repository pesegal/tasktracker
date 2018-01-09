"""
    This module contains all the logic to communicate data with the database.
"""

import os
import os.path
import shutil
import sqlite3
from datetime import datetime, timezone
from functools import partial
from queue import Queue
from threading import Thread

from kivy.clock import Clock

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
# Note this number should be updated everytime the db schema is changed
# it is used on database file load to make sure that the file is correctly formatted.
__database_version_number__ = '00001'


def load_file_check_version(loaded_file_path):
    """ Takes the path of loaded db file and checks the table
        to make sure that it is of the correct version and format.
        :return True if file valid else False
    """
    version_number = ''
    try:
        con = sqlite3.connect(loaded_file_path)
        cur = con.cursor()
        cur.execute("select version_number from tasktracker")
        version_number = cur.fetchone()[0]
        con.close()
    except sqlite3.DatabaseError:
        return False

    if con:
        con.close()

    return version_number == __database_version_number__


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

    def backup_database(self, controller, create_backup_path=None, load_backup_path=None):
        """ This function creates a backup of the sqlite database by copying the
            dbfile. This shuts down the db thread and restarts the db thread after copying
            to avoid file corruption.

            If create backup path is populated this set the source path to the current database path
            in self._database_backup function, if load_backup_path is populated then the destination
            path in self._database_backup will be set to self.path.

            :param controller - reference to the object calling db_backup. For error notifications.
            :param create_backup_path - full path and filename for the db backup.
            :param load_backup_path - used when loading from backup (the backup file)

        """
        if self.db_thread.is_alive():
            self.action_queue.put(
                SqlTask(statement='shutdown',
                        callback=self._database_backup,
                        args=(controller, create_backup_path, load_backup_path)
                        )
            )

    def _database_backup(self, arguments, dt):
        """ Callback to do the database copy once the thread has shutdown """
        obj = arguments[0]
        destination_path = arguments[1] if arguments[1] is not None else self.path
        source_path = arguments[2] if arguments[2] is not None else self.path

        try:
            shutil.copyfile(source_path, destination_path)

        except OSError as os_err:
            # Write permissions don't exist.
            obj.error_popup(str(os_err))

        except shutil.SameFileError as sf_err:
            # When self.path = dst_path
            obj.error_popup(str(sf_err))

        finally:
            self.thread_startup()

    def thread_status(self):
        print("Thread is alive: ", self.db_thread.is_alive(), self.db_thread.ident)

    def thread_startup(self):
        """ if the thread is dead """
        if not self.db_thread.is_alive():
            # You cannot restart a stopped thread due to os limitations. Creating new thread instead.
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
        # self.action_queue.join() # TODO: This was causing the softlock WHY? IS THIS REQUIRED?

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

    def get_task_actions_stats(self, start_time, end_time, callback):
        self.action_queue.put(
            SqlTask(
                """
                    SELECT
                        ta.id,
                        ta.creation_date,
                        ta.finish_date,
                        strftime('%s', ta.finish_date) - strftime('%s', ta.creation_date) AS period_seconds,
                        aty.action_description,
                        t.id as task_id,
                        t.name as task_name,
                        p.id as project_id,
                        p.name as project_name

                    FROM task_actions AS ta
                    JOIN tasks AS t ON ta.task_id = t.id
                    JOIN action_type AS aty ON ta.action_id = aty.id
                    JOIN projects AS p ON t.project_id = p.id
                    WHERE ta.creation_date >= ? AND finish_date <= ?;
                """,
                args=(start_time, end_time),
                function='fetchall',
                callback=callback
            )
        )

    def get_action_type(self, type_id, callback):
        self.action_queue.put(
            SqlTask('SELECT action_description FROM action_type WHERE id = ?;',
                    args=(type_id,),
                    function='fetchone',
                    callback=callback)
        )

    def get_task_actions_for_flat_file(self, callback):
        self.action_queue.put(
            SqlTask(
                """
                    SELECT
                        tasks.name AS "Task Name",
                        projects.name AS "Project Name",
                        action_type.action_description AS "Action Type",
                        task_actions.creation_date AS "Action Start",
                        task_actions.finish_date AS "Action End",
                        strftime('%s', task_actions.finish_date) -
                        strftime('%s', task_actions.creation_date) AS "Action Duration (sec)"
                    FROM task_actions
                    JOIN action_type ON action_type.id = task_actions.action_id
                    JOIN tasks ON task_actions.task_id = tasks.id
                    JOIN projects ON tasks.project_id = projects.id
                    ORDER BY task_actions.creation_date;
                """,
                function='fetchall',
                callback=callback
            )
        )

    def delete_project(self, project):
        pass

DB = Database(os.path.join(__location__, 'tt_dev.db'))
