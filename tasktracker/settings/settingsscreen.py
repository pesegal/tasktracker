
from tasktracker.themes import themes
from tasktracker.themes.themes import Themeable, THEME_CONTROLLER, NOTIFICATION_SOUND

from kivy.uix.screenmanager import Screen

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton, ToggleButtonBehavior
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock


class SettingsScreen(Screen, Themeable):
    """ Settings screen object contains all of the control logic relating to the settings screen
    The layout information of the settings screen is located in the 'settings_screen.kv' file in the layouts
    directory.
    """

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)

    def theme_update(self):
        pass


class SettingsSoundSelector(Spinner, Themeable):
    """ Contains all the dropdown functionality to allow users to select a different notification
    sound. Sound loading and control are contained in global object NOTIFICATION_SOUND in themes.py
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sounds = NOTIFICATION_SOUND.loaded_sounds
        self.text = NOTIFICATION_SOUND.start_sound
        self.values = [s[0] for s in self.sounds]

        self.bind(text=self.select_new_sound)

    def select_new_sound(self, obj, text):
        sound_path_index = list(zip(*self.sounds))[0].index(text)  # gets the index of the full path
        self._load_new_notification_sound(*self.sounds[sound_path_index])

    def _load_new_notification_sound(self, soundname, sound_path, preview=True):
        NOTIFICATION_SOUND.load(soundname, sound_path)
        if preview:
            NOTIFICATION_SOUND.play()

    def theme_update(self):
        pass


class SettingsSoundVolumeSlider(Slider, Themeable):
    """ Sets the volume of the notification sound from 0 to 1.
    Notification sound information is contained inside the SoundController class.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.min = 0
        self.max = 100
        self.value = NOTIFICATION_SOUND.volume
        self.bind(value=self._change_volume)

    def _change_volume(self, obj, vol):
        print(obj, vol)
        NOTIFICATION_SOUND.set_volume(vol)
        NOTIFICATION_SOUND.play()
        # Clock.schedule_once(NOTIFICATION_SOUND.stop, .05)

    def theme_update(self):
        pass


class SettingsContainer(BoxLayout, Themeable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        pass


class ThemeSettingsContainer(SettingsContainer):
    """ Dynamically adds theme selection from configuration file."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(SettingsLabel(text='Theme Selection:'))
        for theme_name in [theme.name for theme in THEME_CONTROLLER.theme_list]:
            if theme_name == THEME_CONTROLLER.default_theme:
                self.add_widget(ThemeSelectionToggleButton(text=theme_name, group='theme_selection', state='down'))
            else:
                self.add_widget(ThemeSelectionToggleButton(text=theme_name, group='theme_selection'))


class SettingsButton(Button, Themeable):
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


class ThemeSelectionToggleButton(SettingsToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        THEME_CONTROLLER.set_theme(self.text)
        THEME_CONTROLLER.set_theme_default(self.text)


class SettingsLabel(Label, Themeable):
    text_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        text_c = self.theme.text
        text_c[3] = .8
        self.color = text_c

    def theme_update(self):
        text_c = self.theme.text
        text_c[3] = .8
        self.color = text_c


