""" Themes module contains all the logic for loading and changing visual themes.
    This data can be loaded both the config files and the atlas information/texture files that will
    be contained in a sub-directory.
"""

from configparser import ConfigParser
from collections import namedtuple
from kivy.uix.widget import Widget
from kivy.properties import ListProperty
from kivy.utils import get_color_from_hex

from tasktracker.settings import Borg

__theme_config_path__ = './tasktracker/themes/themes.conf'


# Texture Paths todo: replace with atlas
__project_indicator__ = './themes/gfx/all_white3.png'
__shadow__ = './themes/gfx/shadow.png'
__task_texture__ = './themes/gfx/all_white3.png'

# Config Setup

# Global Color Helpers
__transparent__ = [1, 1, 1, 0]


# Theme Object Definitions
Theme = namedtuple('Theme', 'name, status, listbg, background, tasks, text')


# TODO: Dynamically Load in themes so that all of the tags change correctly.

class ThemeController(Borg, Widget):
    """ The theme controller is a singleton that handles all of the color scheme loading
        and changing of data.
    """
    # Theme Color Property Initialization
    status = ListProperty()
    list_bg = ListProperty()
    background = ListProperty()
    tasks = ListProperty()
    text = ListProperty

    def __init__(self):
        super().__init__()
        self.theme_list = list()
        self._load_theme_configuration()
        self.set_theme('Light Theme')

    def _load_theme_configuration(self):
        config = ConfigParser()
        config.read(__theme_config_path__)
        themes = config.sections()
        for theme in themes:
            value_list = list()
            for k, v in config[theme].items():
                value_list.append(get_color_from_hex(v))
            self.theme_list.append(Theme(theme, *value_list))

    def set_theme(self, theme_name):
        print(theme_name)
        for theme in self.theme_list:
            if theme.name == theme_name:
                self.status = theme.status
                self.list_bg = theme.listbg
                self.background = theme.background
                self.tasks = theme.tasks
                self.text = theme.text


__Theme__ = ThemeController()
