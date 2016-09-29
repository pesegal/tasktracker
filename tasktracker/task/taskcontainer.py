"""
    Tasklist that handles the ordering and displaying of objects.
"""
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
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
    """ Wraps the ListNameLabelDisplay and provides the scrolling functionality."""
    scroll_bg_color = ListProperty()

    def __init__(self, list_id, name='none', **kwargs):
        super(TaskScrollContainer, self).__init__(**kwargs)
        self.drop_type = 'scroll_list'
        self.list_id = list_id
        self.name = name
        self.task_list = TaskList(self.list_id)
        self.label_view = ListNameLabelDisplay(self.task_list)
        self.label_view.add_widget(self.task_list)
        self.add_widget(self.label_view)
        self.label_view.pos = self.pos
        self.bind(height=self._size_update)
        self.theme_update()
        print("Scroll Height:", self.height)

    def theme_update(self):
        self.scroll_bg_color = self.theme.list_bg

    def _size_update(self, widget, height):
        self.label_view.resize_height(widget, height)
        print("Scroll Height:", self.height)


class ListNameLabelDisplay(RelativeLayout):

    def __init__(self, task_list, **kwargs):
        super().__init__(**kwargs)
        self.list_label = None
        self.task_list = task_list
        self.global_y = self.to_widget(self.x, -20, relative=False)[1]
        print("Init Global_Y: ", self.global_y)

    # TODO: Look into the removing of the widgets and when the height changes.

    def show_label(self):
        if self.height > self.parent.height:
            print("Widget Relative: ", self.parent.name, self.to_widget(0, -20, relative=True))
            print("Layout Height: ", self.parent.name, self.height, self.parent.height)
            print(self.global_y)

        self.list_label = ListLabels(text=self.parent.name.capitalize(),
                                     pos=(self.x, self.global_y))
        self.list_label.height = 0
        label_animation = Animation(pos=(self.x, self.global_y + 40),
                                    duration=.2, t='in_quad')
        self.add_widget(self.list_label)
        label_animation.start(self.list_label)

    def remove_label(self):
        global_y = self.to_widget(self.x, -20, relative=True)[1]
        label_animation = Animation(pos=(self.x, self.global_y), duration=.2, t='out_quad')
        label_animation.bind(on_complete=lambda *args: self.remove_widget(self.list_label))
        label_animation.start(self.list_label)

    def resize_height(self, widget, height):
        self.global_y = self.to_widget(self.x, -20 , relative=True)[1]
        print("Sized Global_y: ", self.global_y)
        if widget is self.task_list:
            if height < self.parent.height:
                self.height = self.parent.height
            else:
                self.height = self.task_list.height
        else:
            if height < self.task_list.height:
                self.height = self.task_list.height
            else:
                self.height = self.parent.height


class TaskList(GridLayout):
    def __init__(self, list_id, **kwargs):
        super(TaskList, self).__init__(**kwargs)
        self.drop_type = 'tasklist'
        self.list_id = list_id
        self.bind(minimum_height=self.setter('height'))
        self.bind(height=self._update_parent_height)

        self.list_label = None

    def update_list_positions(self):
        for index, child in enumerate(self.children):
            DB.update_task_list_index(index, child.uuid)

    def _update_parent_height(self, widget, height):
        print("Task list trigger: ")
        self.parent.resize_height(widget, height)





