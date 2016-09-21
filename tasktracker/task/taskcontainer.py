"""
    Tasklist that handles the ordering and displaying of objects.
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty
from kivy.utils import get_color_from_hex
from tasktracker.themes.themes import Themeable

from tasktracker.database.db_interface import DB


class TaskScrollContainer(ScrollView, Themeable):
    scroll_bg_color = ListProperty(get_color_from_hex('#F5F5F5'))
    # todo: Replace with theme color loader

    def __init__(self, list_id, name='none', **kwargs):
        super(TaskScrollContainer, self).__init__(**kwargs)
        self.drop_type = 'scroll_list'
        self.list_id = list_id
        self.name = name
        self.task_list = TaskList(self.list_id)
        self.add_widget(self.task_list)
        self.theme_update()

    def theme_update(self):
        self.scroll_bg_color = self.theme.list_bg


class TaskList(GridLayout):
    def __init__(self, list_id, **kwargs):
        super(TaskList, self).__init__(**kwargs)
        self.drop_type = 'tasklist'
        self.list_id = list_id
        self.bind(minimum_height=self.setter('height'))

    def update_list_positions(self):
        for index, child in enumerate(self.children):
            DB.update_task_list_index(index, child.uuid)

