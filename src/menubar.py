"""
    The Menu Bar task will be listed at the bottom of the screen
    this menu will provide the ability to create new tasks and switch
    to other screens for example, the timer screen and the statistics
    screen.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from src.taskcontainer import TaskCreationScreen

Builder.load_file('./src/menubar.kv')


class MenuBar(BoxLayout):
    def __init__(self, **kwargs):
        super(MenuBar, self).__init__(**kwargs)

    def create_new_task(self, *args):
        TaskCreationScreen().open()

    def print_stuff(self, *args):
        print('test:', self.get_root_window().children)

    def switch_screens(self, name, direction):
        self.parent.screen_controller.transition.direction = direction
        self.parent.screen_controller.current = name

    def switch_lists(self, direction):
            self.parent.broadcast_child('slide_task_lists', direction=direction)











