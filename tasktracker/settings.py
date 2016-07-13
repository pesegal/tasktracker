"""
    Settings contains global configuration settings. This is where .conf files will be loaded and global shared
    variables will live.
"""
import os
from configparser import ConfigParser
from kivy.utils import get_color_from_hex

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


__project_colors__ = Colors('colors.conf')