"""
    The Menu Bar task will be listed at the bottom of the screen
    this menu will provide the ability to create new tasks and switch
    to other screens for example, the timer screen and the statistics
    screen.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
from kivy.properties import ObjectProperty, StringProperty, ListProperty

from tasktracker.mixins import Broadcast
from tasktracker.task.taskpopups import TaskCreationScreen
from tasktracker.themes import themes
from tasktracker.themes.themes import Themeable


class MenuBar(BoxLayout, Broadcast, Themeable):
    current_screen = StringProperty('tasks')
    menu_bar_bg_color = ListProperty()

    def __init__(self, **kwargs):
        super(MenuBar, self).__init__(**kwargs)
        self.bind(current_screen=self.screen_state_change)
        self.scroll_list_left = MenuButton(text='<<', on_press=lambda x: self.switch_lists('left'))
        self.scroll_list_right = MenuButton(text='>>', on_press=lambda x: self.switch_lists('right'))
        self.theme_update()
        # self.add_widget(self.scroll_list_left, index=len(self.children))
        # self.add_widget(self.scroll_list_right, index=0)

        # Menu Button Text Storage
        self.task_text = self.ids.task_button.text
        self.timer_text = self.ids.timer_button.text
        self.stats_text = self.ids.stats_button.text
        self.settings_text = self.ids.settings_button.text

        self.delete_color = get_color_from_hex('#e53935')

    def theme_update(self):
        self.menu_bar_bg_color = self.theme.status

    def start_drag_menu_button_text(self):
        # This function adjusts the menu buttons display for click drag action.
        self.ids.task_button.text = 'EDIT TASK'
        self.ids.timer_button.text = 'WORK'
        self.ids.stats_button.text = 'INSPECT'

        # TODO: Look into changing the color of the button to a red for delete.
        self.ids.settings_button.background_color = self.delete_color
        self.ids.settings_button.text = 'DELETE'

    def release_drag_menu_button_text(self):
        self.ids.task_button.text = self.task_text
        self.ids.timer_button.text = self.timer_text
        self.ids.stats_button.text = self.stats_text

        # Todo: Reset settings button color!
        self.ids.settings_button.background_color = self.ids.settings_button.bg_color
        self.ids.settings_button.text = self.settings_text

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
            self.ids.task_button.text = self.task_text
            self._add_scroll_buttons()
        else:
            self.ids.task_button.text = 'TASKS'
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

    def change_theme(self):
        # Temporary to test the theme changes. TODO: Remove when settings menu is created.
        if themes.THEME_CONTROLLER.theme_name == 'Dark Theme':
            themes.THEME_CONTROLLER.set_theme('Light Theme')
        else:
            themes.THEME_CONTROLLER.set_theme('Dark Theme')


class MenuButton(Button, Themeable):
    menu = ObjectProperty(None)
    drop_type = StringProperty()
    text_color = ListProperty()
    press_color = ListProperty()
    button_texture = StringProperty(themes.MENUBUTTON_TEXTURE)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_update()
        self.bg_color = [0, 0, 0, 0]
        self.background_normal = ''

    def theme_update(self):
        self.text_color = self.theme.text
        self.press_color = self.theme.menu_down
        self.press_color[3] = .4
        self.text_color[3] = .88

    def on_press(self):
        self.background_color = self.press_color

    def on_release(self):
        self.background_color = self.bg_color

    def execute_function(self, function):
        pass


class SwitchScreenButton(Button):
    pass
