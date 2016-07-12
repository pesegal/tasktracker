"""
    Author: Peter Segal
    Todo List Plus

"""
import os
from kivy.app import App
from kivy.lang import Builder
from tasktracker.screencontroller import ScreenClickDragWindow

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Load in the .kv files
layout_path = os.path.join(__location__, 'layouts')


class TaskApp(App):
    def build(self):
        self.title = 'TaskTracker++'
        self.minimum_width = 150
        self.minimum_height = 300
        return ScreenClickDragWindow()

if __name__ == '__main__':
    # Load KV
    for file in os.listdir(layout_path):
        Builder.load_file(os.path.join(layout_path, file))
    # Load configurations
    TaskApp().run()
