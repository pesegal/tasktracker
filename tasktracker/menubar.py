"""
    The Menu Bar task will be listed at the bottom of the screen
    this menu will provide the ability to create new tasks and switch
    to other screens for example, the timer screen and the statistics
    screen.
"""

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from tasktracker.broadcast import BroadcastMixin
from tasktracker.task.taskcontainer import TaskCreationScreen


class MenuBar(BoxLayout, BroadcastMixin):
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

    def width_state_change(self, **kwargs):
        screen_state = kwargs['width_state']
        if screen_state == 4:
            self.remove_widget(self.ids.scroll_list_left)
            self.remove_widget(self.ids.scroll_list_right)
        elif screen_state is not 4 and self.ids.scroll_list_left not in self.children:
            self.add_widget(self.ids.scroll_list_left, index=len(self.children))
            self.add_widget(self.ids.scroll_list_right, index=0)










