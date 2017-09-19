
from tasktracker.themes import themes
from tasktracker.themes.themes import Themeable, THEME_CONTROLLER, NOTIFICATION_SOUND, CONFIG_PARSER
from tasktracker.database.db_interface import DB

from kivy.uix.screenmanager import Screen

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton, ToggleButtonBehavior
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.clock import Clock

import os


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
        NOTIFICATION_SOUND.set_volume(vol)
        NOTIFICATION_SOUND.play()
        # Clock.schedule_once(NOTIFICATION_SOUND.stop, .05)

    def theme_update(self):
        pass


class SettingsPopup(Popup, Themeable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.5, .3)

    def theme_update(self):
        pass


class SettingsContainer(BoxLayout, Themeable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        pass


class ConfirmationNotification(SettingsContainer):
    popup = ObjectProperty(None)
    controller = ObjectProperty(None)
    notification_message = StringProperty("Notification")
    file_path = StringProperty('/')

    def __init__(self, popup, message, controller=None, file_path='', **kwargs):
        super().__init__(**kwargs)
        self.popup = popup
        self.notification_message = message
        self.file_path = file_path
        self.controller = controller


class ErrorNotification(SettingsContainer):
    popup = ObjectProperty(None)
    error_message = StringProperty("ERROR")

    def __init__(self, popup, message, **kwargs):
        super().__init__(**kwargs)
        self.popup = popup
        self.error_message = message


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


class BackupSettingsContainer(SettingsContainer):
    """ Contains the controller information relating to the db backup functionality."""
    selected_path = StringProperty('/')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_chooser = Factory.FileSaveLoadController()
        self.selected_path = os.path.expanduser('~')

    def open_selection_backup(self, *args):
        print("_open_selection_backup", args)
        self.file_chooser.show_save(callback=self._set_path_and_file, start_path=self.selected_path)

    def _set_path_and_file(self, path, filename):
        self.selected_path = path
        full_file_path = os.path.join(path, filename)
        print(filename)

        # Do Duplicate filename check and open up confirmation window.
        if os.path.isfile(full_file_path):
            popup = SettingsPopup(title='File Exists')
            content = ConfirmationNotification(
                popup=popup,
                message="Filename %s exists. Overwrite?" % os.path.basename(filename),
                file_path=full_file_path,
                controller=self
            )
            popup.content = content
            self.open_selection_backup()
            popup.open()
        else:
            self._backup_database(full_file_path)

    def _backup_database(self, full_file_path):
        DB.backup_database(self, full_file_path)
        DB.thread_status()

    def error_popup(self, error):
        """ Called to open a popup upon error on database file backup."""
        self.open_selection_backup()
        popup = SettingsPopup(title='File Backup Error')
        content = ErrorNotification(
            popup=popup,
            message=error
        )
        popup.content = content
        popup.open()


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


