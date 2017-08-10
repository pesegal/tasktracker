""" Themes module contains all the logic for loading and changing visual themes.
    This data can be loaded both the config files and the atlas information/texture files that will
    be contained in a sub-directory.
"""

import weakref
import os
from configparser import ConfigParser
from collections import namedtuple
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, StringProperty
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.core.audio import SoundLoader

from tasktracker.settings.settingscontroller import Borg

_theme_path = os.path.dirname(__file__)
__theme_config_path__ = _theme_path + '/themes.conf'

# Texture Paths todo: replace with atlas
NO_BEV_CORNERS = _theme_path + '/gfx/all_white.png'
ALL_BEV_CORNERS = _theme_path + '/gfx/all_white2.png'
LEFT_BEV_CORNERS = _theme_path + '/gfx/all_white3.png'
SHADOW_TEXTURE = _theme_path + '/gfx/shadow.png'
BEV_SHADOW_TEXTURE = _theme_path + '/gfx/beveled_shadow.png'
TRANSPARENT_TEXTURE = _theme_path + '/gfx/transparent.png'

# Notification Sound Paths
NOTIFICATION_SOUND = SoundLoader.load(_theme_path + '/sounds/notification.wav')

# Config Setup

# Global Color Helpers
TRANSPARENT   = [1, 1, 1, 0]
SHADOW_COLOR  = [0, 0, 0, .5]

# Theme Object Definitions
Theme = namedtuple('Theme', 'name, status, listbg, background, tasks, text, menudown, selected')


class Themeable:
    def __init__(self):
        self.theme = THEME_CONTROLLER
        self.theme.register(weakref.ref(self))

    def theme_update(self):
        raise NotImplementedError('Themeable widget (%s) need to implement a theme_update method.' %
                                  self.__class__.__name__)


class ThemeController(Borg, Widget):
    """ The theme controller is a singleton that handles all of the color scheme loading
        and changing of data.
    """
    # Theme Color Property Initialization
    theme_name = StringProperty()
    status = ListProperty()
    list_bg = ListProperty()
    background = ListProperty()
    tasks = ListProperty()
    text = ListProperty()
    menu_down = ListProperty()

    def __init__(self):
        super().__init__()
        self.config = ConfigParser()
        self.theme_list = list()
        self.default_theme = None
        self._load_theme_configuration()
        self.registry = list()

        self.set_theme(self.default_theme)  # Stored Configuration Settings Loaded Here

    def _load_theme_configuration(self):
        self.config.read(__theme_config_path__)
        themes = self.config.sections()
        for theme in themes:
            if theme == 'default':  # Get the default theme from the configuration file.
                self.default_theme = self.config['default']['defaulttheme']
                continue
            value_list = list()
            for k, v in self.config[theme].items():
                value_list.append(get_color_from_hex(v))
            self.theme_list.append(Theme(theme, *value_list))

    def set_theme(self, theme_name):
        """ Sets the theme by name. If theme name not in valid list of themes defaults to first theme."""
        if theme_name not in [theme.name for theme in self.theme_list]:
            self.theme_name = self.theme_list[0].name
        else:
            self.theme_name = theme_name

        for theme in self.theme_list:
            if theme.name == self.theme_name:
                self.status = theme.status
                self.list_bg = theme.listbg
                self.background = theme.background
                self.tasks = theme.tasks
                self.text = theme.text
                self.menu_down = theme.menudown
                self.selected = theme.selected

        Window.clearcolor = list(self.background)
        self._broadcast_theme_changes()

    def set_theme_default(self, theme_name):
        self.config['default']['defaulttheme'] = theme_name
        with open(__theme_config_path__, 'w') as configfile:  # save the date to the .conf
            self.config.write(configfile)
        self.theme_name = theme_name

    def register(self, ref):
        self.registry.append(ref)

    def _flush(self):
        to_remove = []

        for ref in self.registry:
            if ref() is None:
                to_remove.append(ref)

        for item in to_remove:
            self.registry.remove(item)

    def _broadcast_theme_changes(self):
        self._flush()

        for widget in self.registry:
            widget().theme_update()


THEME_CONTROLLER = ThemeController()
