"""
    Tasklist that handles the ordering and displaying of objects.
"""

from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.utils import get_color_from_hex

from tasktracker.database.db_interface import db
from tasktracker.settings import __project_colors__
from tasktracker.task.task import Task


class Project:
    def __init__(self, id, creation, deletion, name, color):
        self.db_id = id
        self.name = name
        self.creation_date = creation
        self.deletion_date = deletion
        self.color = color

    def create_project(self):
        pass

    def update_project(self):
        pass

    def delete_project(self):
        pass


class ProjectSelector(Spinner):
    def __init__(self, **kwargs):
        super(ProjectSelector, self).__init__(**kwargs)
        self.values = list()
        self.project_list = list()

        self.load_all_projects()
        self.text = self.project_list[0].name

        self.populate_values()

    def load_all_projects(self):
        projects = db.load_all_projects()
        for project in projects:
            self.project_list.append(Project(*project))

    def select_project(self):
        pass

    def populate_values(self):
        self.values = list()
        for project in self.project_list:
            self.values.append(project.name)


class ProjectPopup(Popup):
    def __init__(self, **kwargs):
        super(ProjectPopup, self).__init__(**kwargs)
        self.ids.color_selector.load_color_buttons()


class ColorSelectionWindow(GridLayout):
    def __int__(self, **kwargs):
        super(ColorSelectionWindow, self).__init__(**kwargs)
        self.resize_flag = False

    def load_color_buttons(self):
        self.cols = 11
        for name, color in __project_colors__.get_name_and_hex_values():
            self.add_widget(ColorSelectionButton(name, color))


class ColorSelectionButton(ToggleButton):
    def __init__(self, name, color, **kwargs):
        super(ColorSelectionButton, self).__init__(**kwargs)
        self.name = name
        self.group = 'color_selections'
        self.hex = color
        self.background_color = get_color_from_hex(color)

        # Todo: Return the color hex and the names of colors.


# --- Logic for Task Screens ---

class TaskScreen(Popup):
    task_name = ObjectProperty(None)
    list_selection = NumericProperty(0)
    project_selection = NumericProperty(0)
    notes = ObjectProperty(None)


class TaskCreationScreen(TaskScreen):
    def __init__(self, **kwargs):
        super(TaskCreationScreen, self).__init__(**kwargs)

    def create_task(self):
        t_list = self.parent.children[1].children[0].screen_controller.tasks  # can this be done better?
        new_task_index = t_list.get_list_length(self.list_selection)
        task_id = db.add_new_task(self.task_name.text, self.notes.text, self.list_selection,
                                  new_task_index, self.project_selection)
        task = Task(task_id, self.task_name.text, self.notes.text)
        t_list.add_task_to_list(task, self.list_selection)
        self.dismiss()


class TaskEditScreen(TaskScreen):  # Need to figure out how to open the task screen!
    def __init__(self, task, **kwargs):
        super(TaskEditScreen, self).__init__(**kwargs)
        self.list_changed_flag = False
        self._load_task_data(task.uuid)
        self.task = task

    def _load_task_data(self, task_id):
        task_data = db.load_task_data(task_id)
        self.task_name.text = task_data[6]
        self.notes.text = task_data[7]

        self.list_selection = task_data[4] - 1
        if self.list_selection == 0:
            self.ids.today_button.state = 'down'
        elif self.list_selection == 1:
            self.ids.tomorrow_button.state = 'down'
        elif self.list_selection == 2:
            self.ids.future_button.state = 'down'
        elif self.list_selection == 3:
            self.ids.archive_button.state = 'down'

        # Future Project Selection Information here!
        self.project_selection = task_data[3]

        self.bind(list_selection=self.updated_list_flag)

    def update_task(self):
        if self.list_changed_flag:
            task_list_screen = self.task.parent.parent.parent.parent
            self.task.parent.remove_widget(self.task)
            task_list_screen.add_task_to_list(self.task, self.list_selection)
            db.task_switch(self.task.uuid, self.list_selection)
            self.task.parent.update_list_positions()

        # Update task in the database
        db.update_task(self.task.uuid, self.task_name.text, self.notes.text, self.project_selection)
        # Update task in the current session
        self.task.text = self.task_name.text
        self.task.notes = self.notes.text
        self.task.project_id = self.project_selection

        self.dismiss()

    def updated_list_flag(self, *args):
        self.list_changed_flag = True
        print("IT MOVED!")


class ProjectSelectionSection(BoxLayout):
    def open_project_screen(self):
        ProjectPopup().open()


class TaskListSelectionButton(ToggleButton):
    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)


class TaskScrollContainer(ScrollView):
    def __init__(self, list_id, name='none', **kwargs):
        super(TaskScrollContainer, self).__init__(**kwargs)

        # Test to add something to display information!
        self.drop_type = 'scroll_list'
        self.list_id = list_id
        self.name = name
        self.task_list = TaskList(self.list_id)
        self.add_widget(self.task_list)


class TaskList(GridLayout):
    def __init__(self, list_id, **kwargs):
        super(TaskList, self).__init__(**kwargs)
        self.drop_type = 'tasklist'
        self.list_id = list_id
        self.cols = 1
        self.spacing = 1
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

    def update_list_positions(self):
        for index, child in enumerate(self.children):
            db.update_task_list_index(index, child.uuid)
