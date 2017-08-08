
from tasktracker.themes import themes
from tasktracker.themes.themes import Themeable

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton, ToggleButtonBehavior
from kivy.properties import StringProperty, ListProperty


class SettingsScreen(Screen, Themeable):
    """ Settings screen object contains all of the control logic relating to the settings screen
    The layout information of the settings screen is located in the 'settings_screen.kv' file in the layouts
    directory.
    """

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)



class SettingsContainer(BoxLayout, Themeable):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        pass


class SettingsToggleButton(ToggleButton, Themeable):
    button_texture = StringProperty(themes.ALL_BEV_CORNERS)
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    text_color = ListProperty()
    button_color = ListProperty()
    shadow_color = ListProperty()

    def theme_update(self):
        self.button_color = self.theme.tasks
        text = self.theme.text
        text[3] = .8
        self.text_color = text
        self.on_state(self, 0)

    def on_state(self, widget, value):
        if self.state == 'down':
            self.button_color = self.theme.selected
        else:
            self.button_color = self.theme.tasks

    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)

