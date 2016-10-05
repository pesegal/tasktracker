"""
    Tasklist that handles the ordering and displaying of objects.
"""
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty, StringProperty
from tasktracker.themes.themes import Themeable
from tasktracker.themes.themes import MENUBUTTON_TEXTURE
from kivy.animation import Animation

from tasktracker.database.db_interface import DB


class ListLabels(Label, Themeable):
    shadow_texture = StringProperty(MENUBUTTON_TEXTURE)
    shadow_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shadow_color = self.theme.background
        self.shadow_color[3] = .9

    def theme_update(self):
        self.color = self.theme.text
        self.shadow_color = self.theme.list_bg
        self.shadow_color[3] = .8


class TaskScrollContainer(ScrollView, Themeable):
    """ Wraps the ListNameLabelDisplay and provides the scrolling functionality."""
    scroll_bg_color = ListProperty()

    def __init__(self, list_id, name='none', **kwargs):
        super(TaskScrollContainer, self).__init__(**kwargs)
        self.drop_type = 'scroll_list'
        self.list_id = list_id
        self.name = name
        self.task_list = TaskList(self.list_id)
        self.label_view = ListNameLabelDisplay(self.task_list, self.name)
        self.label_view.add_widget(self.task_list)
        self.add_widget(self.label_view)
        self.label_view.pos = self.pos
        self.bind(height=self._height_update)
        self.theme_update()

    def theme_update(self):
        self.scroll_bg_color = self.theme.list_bg

    def _height_update(self, widget, height):
        self.label_view.resize_height(widget, height)


class ListNameLabelDisplay(FloatLayout):
    def __init__(self, task_list, name, **kwargs):
        super().__init__(**kwargs)
        self.list_label = None
        self.label_active = False
        self.name = name
        self.task_list = task_list
        self.task_height = 60
        self.bind(size=self._update_label_position)
        self.bind(height=self._update_global_y)

    def _update_global_y(self, *args):
        self.global_y = self.to_widget(self.x, -20, relative=True)[1]

    def show_label(self, last_list):
        self._update_global_y()
        if self.height > self.parent.height and last_list.list_id == self.task_list.list_id:
            self.global_y -= (self.task_height * self.parent.scroll_y)
        self.label_active = True
        self.list_label = ListLabels(text=self.name.capitalize())
        x_pos = self.center_x - self.list_label.width / 2
        self.list_label.pos = (x_pos, self.global_y)
        label_animation = Animation(pos=(x_pos, self.global_y + 40), duration=.2, t='out_quad')
        self.add_widget(self.list_label)

        label_animation.start(self.list_label)

    def remove_label(self, new_list):
        self._update_global_y()
        if self.task_list.height + self.task_height > self.parent.height and new_list.list_id == self.task_list.list_id:
            self.global_y += (self.task_height * self.parent.scroll_y)  # todo: look here for list display bug
            self.list_label.y += self.task_height
        label_animation = Animation(pos=(self.list_label.x, self.global_y), duration=.2, t='out_quad')
        label_animation.bind(on_complete=lambda *args: self.remove_widget(self.list_label))
        label_animation.start(self.list_label)
        self.label_active = False

    def _update_label_position(self, *args):
        """ This handles list first drawing when clicking drag sliding to new list.
        note that there will never be a situation when you will need to compensate for list position."""
        if self.label_active:
            if self.height > self.parent.height:
                y_pos = self.height - self.parent.height + 20
            else:
                y_pos = 20
            self.list_label.pos = (self.center_x - self.list_label.width / 2, y_pos)

    def resize_height(self, widget, height):
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
        self.parent.resize_height(widget, height)
