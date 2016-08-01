"""
    The Menu Bar task will be listed at the bottom of the screen
    this menu will provide the ability to create new tasks and switch
    to other screens for example, the timer screen and the statistics
    screen.
"""

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from tasktracker.mixins import Broadcast
from tasktracker.task.taskpopups import TaskCreationScreen


class MenuBar(BoxLayout, Broadcast):
    def __init__(self, **kwargs):
        super(MenuBar, self).__init__(**kwargs)
        self.current_screen = 'tasks'

    def create_new_task(self, *args):
        TaskCreationScreen().open()

    def print_stuff(self, *args):
        print('test:', self.get_root_window().children)

    def switch_screens(self, name, direction):
        self.parent.screen_controller.transition.direction = direction
        self.parent.screen_controller.current = name

    def switch_lists(self, direction):
            self.parent.broadcast_child('slide_task_lists', direction=direction)

    def width_state_change(self, width_state, **kwargs):
        screen_state = width_state
        if screen_state == 4:
            self.remove_widget(self.ids.scroll_list_left.__self__)
            self.remove_widget(self.ids.scroll_list_right.__self__)
        elif screen_state is not 4 and self.ids.scroll_list_left.__self__ not in self.children:
            # TODO: Figure out how to correct bug with weakref object not existing.
            self.add_widget(self.ids.scroll_list_left.__self__, index=len(self.children))
            self.add_widget(self.ids.scroll_list_right.__self__, index=0)


class ScrollButton(Button):
    pass


class MultiUseButton(Button):
    def __init__(self, **kwargs):
        super(MultiUseButton, self).__init__(**kwargs)
        self.drop_type = 'task_edit'



class SwitchScreenButton(Button):
    pass








