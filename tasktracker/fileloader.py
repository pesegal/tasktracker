from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

from tasktracker.themes.themes import CONFIG_PARSER
import os


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    set_popup_title = ObjectProperty(None)
    callback = ObjectProperty(None)
    start_path = StringProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    set_popup_title = ObjectProperty(None)
    callback = ObjectProperty(None)
    start_path = StringProperty(None)


class FileSaveLoadController(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    popup_title = StringProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def set_popup_title(self, path):
        self._popup.title = self.popup_title + ': ' + path

    def show_load(self, popup_title="Load File: ", start_path='/', callback=None):
        self.popup_title = popup_title
        content = LoadDialog(load=self.load, callback=callback, cancel=self,
                             start_path=start_path,
                             set_popup_title=self.set_popup_title)

        self._popup = Popup(title=popup_title + start_path, content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self, popup_title="Save File: ", start_path='/', callback=None):
        self.popup_title = popup_title
        content = SaveDialog(save=self.save, callback=callback, cancel=self,
                             start_path=start_path,
                             set_popup_title=self.set_popup_title)

        self._popup = Popup(title=popup_title + start_path, content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename, callback):
        print(path, filename)

        if callback:
            callback(path, filename)

        # with open(os.path.join(path, filename[0])) as stream:
        #     self.text_input.text = stream.read()

        self.dismiss_popup()

    def save(self, path, filename, callback=None):
        print(path, filename)
        # with open(os.path.join(path, filename), 'w') as stream:
        #     stream.write(self.text_input.text)

        if callback:
            callback(path, filename)
        self.dismiss_popup()


Factory.register('FileSaveLoadController', cls=FileSaveLoadController)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)
