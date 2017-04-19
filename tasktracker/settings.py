"""
    Settings contains global configuration settings. This is where .conf files will be loaded and global shared
    variables will live.
"""
import os
import pytz
import tzlocal

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
    def __init__(self):
        super().__init__()
        self.click_drag_screen = None
        self.task_list_screen = None
        self.timer_screen = None
        self.screen_controller = None
        self.timer_screen = None
        self.timer_task_manager = None
        self.menu_bar = None

# Global Instance Init
APP_CONTROL = AppController()
PROJECT_COLORS = Colors('colors.conf')



""" FUTURE SETTINGS MENU FEATURES

POMODORO TIME
SHORT BREAK TIME
LONG BREAK TIME
STOP WATCH IDLE CHECK

THEME SELECTION

DATABASE RESET

FUTURE: ACCOUNT SELECTION

"""