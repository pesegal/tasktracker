""" Themes module contains all the logic for loading and changing visual themes.
    This data can be loaded both the config files and the atlas information/texture files that will
    be contained in a sub-directory.
"""

from configparser import ConfigParser
from kivy.uix.image import Image

# Texture Paths todo: replace with atlas


__project_indicator__ = './themes/gfx/all_white3.png'
__shadow__ = './themes/gfx/shadow.png'
__task_texture__ = './themes/gfx/all_white3.png'

# Global Color Helpers
__transparent__ = [1, 1, 1, 0]


# TODO: Dynamically Load in themes so that all of the tags change correctly.

class ThemeController:
    """
        The theme controller loads all of the color schemes that can generate
    """
