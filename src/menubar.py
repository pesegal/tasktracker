"""
    The Menu Bar task will be listed at the bottom of the screen
    this menu will provide the ability to create new tasks and switch
    to other screens for example, the timer screen and the statistics
    screen.
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder

Builder.load_file('./src/menubar.kv')


class MenuBar(FloatLayout):
    def __init__(self, **kwargs):
        super(MenuBar, self).__init__(**kwargs)

