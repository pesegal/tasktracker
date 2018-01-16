"""
    Settings contains global configuration settings. This is where .conf files will be loaded and global shared
    variables will live.
"""
import os
import pytz
import tzlocal
import weakref

from configparser import ConfigParser
from kivy.utils import get_color_from_hex
from datetime import datetime

# Timezone conversion functionality

timezone_local = tzlocal.get_localzone()


def to_datetime(datetime_string):
    return datetime.strptime(datetime_string.replace(':', ''), '%Y-%m-%d %H%M%S.%f%z')


def to_local_time(dt):
    return dt.replace(tzinfo=pytz.utc).astimezone(timezone_local)


class Borg:
    """
        The Borg class allows inheritable singleton behavior between all configuration objects.
    """
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state


class Colors(Borg):
    """
        Loads and returns color configuration data in an easy to use format.
    """
    def __init__(self, name):
        super(Colors, self).__init__()
        self.__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.colors = ConfigParser()
        self.colors.read(os.path.join(self.__location__, name))

    def get_hex_values(self):
        for key in self.colors.keys():
            for color in self.colors[key]:
                yield self.colors[key][color]

    def get_name_and_hex_values(self):
        for key in self.colors.keys():
            for color in self.colors[key]:
                yield color, self.colors[key][color]

    def get_kivy_colors(self):
        for key in self.colors.keys():
            for color in self.colors[key]:
                yield get_color_from_hex('#'+self.colors[key][color])

    def get_name_and_kivy_colors(self):
        for key in self.colors.keys():
            for color in self.colors[key]:
                yield color, get_color_from_hex(self.colors[key][color])


class AppController(Borg):
    """ Contains references to important controller objects.
        Also contains the registry for object saving and loading.
    """
    def __init__(self):
        super().__init__()
        self.click_drag_screen = None
        self.task_list_screen = None
        self.timer_screen = None
        self.screen_controller = None
        self.timer_screen = None
        self.timer_task_manager = None
        self.menu_bar = None

        self.data_container_registry = list()

    def register(self, ref):
        self.data_container_registry.append(ref)

    def _flush(self):
        to_remove = list()

        for ref in self.data_container_registry:
            if ref() is None:
                to_remove.append(ref)

        for item in to_remove:
            self.data_container_registry.remove(item)

    def clear_app_data(self):
        """ Calls clear_data function on all objects that are registered
        with the data_container registry.
        """
        self._flush()

        for widget in self.data_container_registry:
            widget().clear_data()

    def load_app_data(self):
        """ Calls the load_data function on all object that are registered
        with the data_container registry.
        """
        self._flush()

        for widget in self.data_container_registry:
            widget().load_data()


class DataContainer:
    """ Mixin class that registers the child classes with the AppController
        and defines the interface for clearing loaded data and reloading data from the database.
    """
    def __init__(self):
        self._appctl = APP_CONTROL
        self._appctl.register(weakref.ref(self))

    def clear_data(self):
        raise NotImplementedError("clear_data method need to be implemented to clear object memory.")

    def load_data(self):
        raise NotImplementedError("load_data method needs to be implemented to load data from db")


class TaskListRegistry:
    """ This object allows program wide objects to look op references to all loaded objects
    in the program.
    """
    def __init__(self):
        self._tasks = list()

    def register(self, item):
        self._tasks.append(weakref.ref(item))

    def _flush(self):
        to_remove = list()

        for ref in self._tasks:
            if ref() is None:
                to_remove.append(ref)

        for item in to_remove:
            self._tasks.remove(item)

    def task_id_lookup(self, task_id):
        """ Returns a weak ref to the task object if task_id == UUID of the task.

        :param task_id: the UUID of the task.
        :return: weakref(Task()) else None if not found
        """
        self._flush()

        for task in self._tasks:
            if task().uuid == task_id:
                return task()

        return None

# Global Instance Init
APP_CONTROL = AppController()
PROJECT_COLORS = Colors('../themes/colors.conf')
ALL_TASKS = TaskListRegistry()


""" FUTURE SETTINGS MENU FEATURES

POMODORO TIME
SHORT BREAK TIME
LONG BREAK TIME
STOP WATCH IDLE CHECK

THEME SELECTION

DATABASE RESET

FUTURE: ACCOUNT SELECTION

"""