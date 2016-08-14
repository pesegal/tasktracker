"""
    The Menu Bar task will be listed at the bottom of the screen
    this menu will provide the ability to create new tasks and switch
    to other screens for example, the timer screen and the statistics
    screen.
"""

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty

from tasktracker.mixins import Broadcast
from tasktracker.task.taskpopups import TaskCreationScreen


class MenuBar(BoxLayout, Broadcast):
    current_screen = StringProperty('tasks')

    def __init__(self, **kwargs):
        super(MenuBar, self).__init__(**kwargs)
        self.bind(current_screen=self.screen_state_change)
        self.scroll_list_left = ScrollButton(text='<<', on_press=lambda x: self.switch_lists('left'))
        self.scroll_list_right = ScrollButton(text='>>', on_press=lambda x: self.switch_lists('right'))
        # self.add_widget(self.scroll_list_left, index=len(self.children))
        # self.add_widget(self.scroll_list_right, index=0)

    def task_multi_use_press(self, *args):
        if self.current_screen == 'tasks':
            TaskCreationScreen().open()
        else:
            self.switch_screens('tasks', 'down')

    def print_stuff(self, *args):
        print('test:', self.get_root_window().children)

    def switch_screens(self, name, direction):
        self.current_screen = name
        self.parent.screen_controller.transition.direction = direction
        self.parent.screen_controller.current = name

    def switch_lists(self, direction):
        self.parent.broadcast_child('slide_task_lists', direction=direction)

    def screen_state_change(self, *args):
        if self.current_screen == 'tasks':
            self.ids.multi_use_button.text = 'New Task'
            self._add_scroll_buttons()
        else:
            self.ids.multi_use_button.text = 'Tasks'
            self._remove_scroll_buttons()

    def width_state_change(self, width_state, **kwargs):
        screen_state = width_state
        if screen_state == 4:
            self._remove_scroll_buttons()
        elif screen_state is not 4 and self.current_screen == 'tasks':
            self._add_scroll_buttons()

    def _add_scroll_buttons(self):
        if self.scroll_list_left not in self.children:
            self.add_widget(self.scroll_list_left, index=len(self.children))
            self.add_widget(self.scroll_list_right, index=0)

    def _remove_scroll_buttons(self):
        if self.scroll_list_left in self.children:
            self.remove_widget(self.scroll_list_left)
            self.remove_widget(self.scroll_list_right)


class ScrollButton(Button):
    def __init__(self, **kwargs):
        super(ScrollButton, self).__init__(**kwargs)
        self.drop_type = None


class MultiUseButton(Button):
    menu = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MultiUseButton, self).__init__(**kwargs)
        self.drop_type = 'task_edit'

    def execute_function(self, function):
        pass



class SwitchScreenButton(Button):
    pass








