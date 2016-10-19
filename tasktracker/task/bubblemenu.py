from kivy.uix.button import Button
from kivy.uix.bubble import Bubble
from kivy.properties import ListProperty, StringProperty

from tasktracker.themes.themes import Themeable
from tasktracker.themes import themes


class TaskQuickMenu(Bubble, Themeable):
    def __init__(self, task, **kwargs):
        super().__init__(**kwargs)
        self.task = task

    def theme_update(self):
        pass


class QuickMenuButton(Button, Themeable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        pass