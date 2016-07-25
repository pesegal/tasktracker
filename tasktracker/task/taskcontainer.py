"""
    Tasklist that handles the ordering and displaying of objects.
"""

from kivy.properties import NumericProperty, ObjectProperty
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
    def __init__(self, id, creation, deletion, name, color, color_name):
        self.db_id = id
        self.name = name
        self.creation_date = creation
        self.deletion_date = deletion
        self.color = color
        self.color_name = color_name

    def update_project(self):
        pass

    def delete_project(self):
        pass


class ProjectSelector(Spinner):
    def __init__(self, **kwargs):
        super(ProjectSelector, self).__init__(**kwargs)
        self.values = list()

        self.bind(text=self.project_change)

    def set_project(self, project):
        self.text = project.name

    def load_projects(self, projects):
        for project in projects:
            self.values.append(project.name)

    def project_change(self, spinner, text):
        self.parent.task_screen.change_project(text)


# TODO: Creating a new project and saving to to database!
# TODO: Get Project loading working! Switching and other stuff needs redesign!


class ProjectPopup(Popup):
    def __init__(self, **kwargs):
        super(ProjectPopup, self).__init__(**kwargs)
        # self.project = project
        self.project_id = None
        self.ids.color_selector.load_color_buttons()
        self.separator_height = 4
        self.edit = False
        self.current_selected_color = None
        self.current_selected_color_name = None

    def update_project_color(self, color_name, color):
        self.title = 'Projects // Color: %s' % color_name.capitalize()
        self.current_selected_color_name = color_name
        self.separator_color = color

    def _load_selected_project_data(self, project_id):
        # Loads the project data into the window if there is project selected.
        project = self.ids.selector.return_project_by_id(project_id)
        self.ids.project_title.text = project.name
        self.ids.color_selector.find_and_select_button(project.color)

    def create_project(self):
        if self.edit:
            pass  # TODO: Add project updating logic here.
        else:
            # Checks for field completeness and creates project.
            name, color = self.ids.project_title.text, self.current_selected_color
            color_name = self.current_selected_color_name
            if name != "" and color:
                db.new_project(name, color, color_name)
                print("Project Created: %s, %s", (name, color))
        self.dismiss()


class ColorSelectionWindow(GridLayout):
    popup = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ColorSelectionWindow, self).__init__(**kwargs)

    def load_color_buttons(self):
        self.cols = 11
        for name, color in __project_colors__.get_name_and_hex_values():
            self.add_widget(ColorSelectionButton(name, color))

    def find_and_select_button(self, hex):
        for child in self.children:
            if child.hex == hex:
                child.state = 'down'
                self.popup.update_project_color(child.name, child.background_color)


class ColorSelectionButton(ToggleButton):
    def __init__(self, name, color, **kwargs):
        super(ColorSelectionButton, self).__init__(**kwargs)
        self.name = name
        self.group = 'color_selections'
        self.hex = color
        self.background_normal = ''
        self.background_color = get_color_from_hex(color)

    def on_press(self):
        self.parent.popup.current_selected_color = self.hex
        self.parent.popup.update_project_color(self.name, self.background_color)

# --- Logic for Task Screens ---


class TaskScreen(Popup):
    task_name = ObjectProperty(None)
    list_selection = NumericProperty(0)
    selected_project = ObjectProperty(None)
    notes = ObjectProperty(None)
    project_popup = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TaskScreen, self).__init__(**kwargs)
        self.project_popup = ProjectPopup()
        self.project_list = list()
        self.load_all_projects()
        self.ids.project_selection_section.ids.selector.set_project(self.project_list[0])
        self.ids.project_selection_section.ids.selector.load_projects(self.project_list)

    def load_all_projects(self):
        projects = db.load_all_projects()
        for project in projects:
            self.project_list.append(Project(*project))

    def change_project(self, text):
        self.selected_project = self.return_project_by_name(text)
        print("New Project Selected: %s" % text)

    def return_project_by_id(self, p_id):
        for project in self.project_list:
            if p_id == project.db_id:
                return project

    def return_project_by_name(self, name):
        for project in self.project_list:
            if name == project.name:
                return project


class TaskCreationScreen(TaskScreen):
    def __init__(self, **kwargs):
        super(TaskCreationScreen, self).__init__(**kwargs)

    def create_task(self):
        t_list = self.parent.children[1].children[0].screen_controller.tasks  # can this be done better?
        new_task_index = t_list.get_list_length(self.list_selection)
        task_id = db.add_new_task(self.task_name.text, self.notes.text, self.list_selection,
                                  new_task_index, self.selected_project.db_id)
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

        # Load correct project!
        self.selected_project = self.return_project_by_id(task_data[3])
        self.ids.project_selection_section.ids.selector.set_project(self.selected_project)

        self.bind(list_selection=self.updated_list_flag)

    def update_task(self):
        if self.list_changed_flag:
            task_list_screen = self.task.parent.parent.parent.parent
            self.task.parent.remove_widget(self.task)
            task_list_screen.add_task_to_list(self.task, self.list_selection)
            db.task_switch(self.task.uuid, self.list_selection)
            self.task.parent.update_list_positions()

        # Update task in the database
        db.update_task(self.task.uuid, self.task_name.text, self.notes.text, self.selected_project.db_id)
        # Update task in the current session
        self.task.text = self.task_name.text
        self.task.notes = self.notes.text
        self.task.project_id = self.selected_project.db_id

        self.dismiss()

    def updated_list_flag(self, *args):
        self.list_changed_flag = True
        print("IT MOVED!")


class ProjectSelectionSection(BoxLayout):
    def open_project_screen(self):
        # send the task project_id or 0 for none
        self.task_screen.project_popup.open()


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
