"""
    Tasklist that handles the ordering and displaying of objects.
"""
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty
from tasktracker.themes.themes import Themeable
from kivy.animation import Animation

from tasktracker.database.db_interface import DB


class ListLabels(Label, Themeable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        self.color = self.theme.text


class TaskScrollContainer(ScrollView, Themeable):
    scroll_bg_color = ListProperty()
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

        self.list_label = None

    def update_list_positions(self):
        for index, child in enumerate(self.children):
            if hasattr(child, 'uuid'):
                DB.update_task_list_index(index, child.uuid)

    def show_label(self):
        self.list_label = ListLabels(text=self.parent.name.capitalize(),
                                     center_x=self.center_x, y=10)
        self.list_label.height = 0
        label_animation = Animation(size=(self.list_label.width, 14), duration=.1, t='in_quad')
        self.add_widget(self.list_label, index=len(self.children))
        label_animation.start(self.list_label)

    def remove_label(self):
        label_animation = Animation(size=(self.list_label.width, 0), duration=.1, t='out_quad')
        label_animation.bind(on_complete=lambda *args: self.remove_widget(self.list_label))
        label_animation.start(self.list_label)


