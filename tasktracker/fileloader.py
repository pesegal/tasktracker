from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

import os


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    callback = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    callback = ObjectProperty(None)


class FileSaveLoadController(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self, popup_title="Load File", callback=None):
        content = LoadDialog(load=self.load, callback=callback, cancel=self.dismiss_popup)
        self._popup = Popup(title=popup_title, content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self, popup_title="Save file", callback=None):
        content = SaveDialog(save=self.save, callback=callback, cancel=self.dismiss_popup)
        self._popup = Popup(title=popup_title, content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename, callback):
        print(path, filename)

        if callback:
            callback(path, filename)

        # with open(os.path.join(path, filename[0])) as stream:
        #     self.text_input.text = stream.read()

        self.dismiss_popup()

    def save(self, path, filename):
        print(path, filename)
        # with open(os.path.join(path, filename), 'w') as stream:
        #     stream.write(self.text_input.text)

        self.dismiss_popup()


Factory.register('FileSaveLoadController', cls=FileSaveLoadController)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)
