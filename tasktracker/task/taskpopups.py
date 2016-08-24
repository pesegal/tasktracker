"""
    Contains all controller logic for the Task Creation/Edit Screens and Project Edit Screens.
"""

from kivy.factory import Factory
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.togglebutton import ToggleButton
from kivy.utils import get_color_from_hex, get_hex_from_color

from tasktracker.database.db_interface import db
from tasktracker.settings import __project_colors__
from tasktracker.task.task import Task


class Project:
    """ Project class is a data structure that contains project data.
    """
    def __init__(self, id, creation, deletion, name, color, color_name):
        self.db_id = id
        self.name = name
        self.creation_date = creation
        self.deletion_date = deletion
        self.color = color
        self.color_name = color_name


class ProjectList:
    """ProjectList Class is a global container that is used to load and track
    modification to project objects.
    """
    def __init__(self):
        super(ProjectList, self).__init__()
        self.project_list = list()
        self.load_all_projects()
        self.default = self.project_list[0]
        self.selected_project = self.default

    def __call__(self):
        return self.project_list

    def load_all_projects(self):
        self.project_list = list()
        projects = db.load_all_projects()
        for project in projects:
            self.project_list.append(Project(*project))

    def change_project_by_id(self, project_id):
        self.selected_project = self.return_project_by_id(project_id)

    def change_project(self, text):
        self.selected_project = self.return_project_by_name(text)

    def return_project_by_id(self, p_id):
        for project in self.project_list:
            if p_id == project.db_id:
                return project

    def return_project_by_name(self, name):
        for project in self.project_list:
            if name == project.name:
                return project


class ProjectSelector(Spinner):
    """ Project Selector contains is the controller functionality for the spinner
    widget that is on the main task screen. The view logic is contained inside
    the taskcontainer.kv layout file.
    """
    def __init__(self, **kwargs):
        super(ProjectSelector, self).__init__(**kwargs)
        self.values = list()
        self.bind(text=self.project_change)
        print("Project Selector Started")

    def set_project(self, project):
        self.text = project.name

    def load_projects(self, projects):
        for project in projects:
            self.values.append(project.name)

    def project_change(self, spinner, text):
        __projects__.change_project(text)
        self.parent.new_project_button_label_update(__projects__.selected_project)
        print("Project Changed")


class ProjectPopupSelector(ProjectSelector):
    """ ProjectPopupSelector contains the controller logic for the project selection spinner widget
        that is inside the ProjectPopup window.
    """
    popup = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ProjectPopupSelector, self).__init__(**kwargs)
        self.values = list()
        self.set_project(__projects__.selected_project)
        print("Project Popup Selecter Started: %s" % __projects__.selected_project.name)
        self.load_projects(__projects__())

    def project_change(self, spinner, text):
        __projects__.change_project(text)
        if self.popup:
            self.popup.set_selected_project(__projects__.selected_project)


class ProjectSpinnerOption(SpinnerOption):
    """ Extending the SpinnerOption widget allows for customization of the drawing of the widget.
    """
    def __init__(self, **kwargs):
        super(ProjectSpinnerOption, self).__init__(**kwargs)
        self.height = 20
        # TODO: Display Projects Selected Colors


class ProjectPopup(Popup):
    """ ProjectPopup is the controller for most of the logic for the project selection and editing.
    popup. This contains the function to trigger creating and updating project records in the database.
    """
    edit = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(ProjectPopup, self).__init__(**kwargs)
        # self.project = project
        self.default_color = [47 / 255., 167 / 255., 212 / 255., 1.]
        self.selected_project = None
        self.project_list = None
        self.ids.color_selector.load_color_buttons()
        self.separator_height = 4
        self.current_selected_color = None
        self.current_selected_color_name = None
        self.bind(edit=self.create_update_button_update)

    def set_project_list(self, projects):
        self.project_list = projects

    def set_selected_project(self, project):
        self.ids.popup_selector.set_project(project)
        self.selected_project = project
        self.current_selected_color = self.selected_project.color
        self.current_selected_color_name = self.selected_project.color_name

        if self.selected_project == __projects__.default:
            self.edit = False
            self.title = 'Create a New Project'
            self.ids.project_title.text = ''
            self.separator_color = self.default_color
        else:
            self.edit = True
            self.update_project_color(self.selected_project.color_name, get_color_from_hex(project.color))
            self.ids.project_title.text = self.selected_project.name

    def update_project_color(self, color_name, color):
        self.title = 'Projects // Color: %s' % color_name.title()
        self.current_selected_color_name = color_name.title()
        self.current_selected_color = get_hex_from_color(color)
        self.separator_color = color
        print("New Color Selected: %s, %s" % (self.current_selected_color, self.current_selected_color_name))

    def create_update_button_update(self, popup, edit):
        if edit:
            self.ids.create_update_button.text = 'Update'
        else:
            self.ids.create_update_button.text = 'New'

    def create_project(self):
        if self.edit:
            self.selected_project.name = self.ids.project_title.text
            self.selected_project.color = self.current_selected_color
            self.selected_project.color_name = self.current_selected_color_name
            db.update_project(self.selected_project)
        else:
            # Checks for field completeness and creates project.
            name, color = self.ids.project_title.text, self.current_selected_color
            color_name = self.current_selected_color_name
            if name != "" and color:
                pid = db.new_project(name, color, color_name)
                __projects__.load_all_projects()
                __projects__.change_project_by_id(pid)
                print("Project Created: %s, %s" % (name, color))
        self.dismiss()


class ColorSelectionWindow(GridLayout):
    """ ColorSelectionWindow is the controller for the multiple diffrent colors one can select for a project.
    """
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
    """ Contains controller functionality for the buttons that show color selection.
    """
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


class TaskScreen(Popup):
    """ This is the parent class for both the new task screen and the task creation screen.
    It contains controller logic that is shared between both types of popups.
    """
    task_name = ObjectProperty(None)
    list_selection = NumericProperty(0)
    selected_project = ObjectProperty(None)
    notes = ObjectProperty(None)
    project_popup = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TaskScreen, self).__init__(**kwargs)
        self.project_popup = ProjectPopup()
        self.ids.project_selection_section.ids.selector.set_project(__projects__.default)
        self.ids.project_selection_section.ids.selector.load_projects(__projects__())
        self.project_popup.bind(on_dismiss=self.project_updated)

    def project_updated(self, popup):
        self.ids.project_selection_section.ids.selector.set_project(__projects__.selected_project)


class TaskCreationScreen(TaskScreen):
    """ TaskCreationScreen is shown when a clicks the create new task button. View logic is contained
    in taskcontainer.kv.
    """
    def __init__(self, **kwargs):
        super(TaskCreationScreen, self).__init__(**kwargs)

    def create_task(self):
        t_list = self.parent.children[1].children[0].screen_controller.tasks  # todo: can this be done better?
        new_task_index = t_list.get_list_length(self.list_selection)
        task_id = db.add_new_task(self.task_name.text, self.notes.text, self.list_selection,
                                  new_task_index, self.selected_project.db_id)
        task = Task(task_id, self.task_name.text, self.notes.text)
        t_list.add_task_to_list(task, self.list_selection)
        self.dismiss()


class TaskEditScreen(TaskScreen):
    """ TaskEditScreen contains controller logic for the editable task screen version of the code.
    """
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
        __projects__.selected_project = __projects__.return_project_by_id(task_data[3])
        self.ids.project_selection_section.ids.selector.set_project(__projects__.selected_project)

        self.bind(list_selection=self.updated_list_flag)

    def update_task(self):
        if self.list_changed_flag:
            task_list_screen = self.task.parent.parent.parent.parent
            self.task.parent.remove_widget(self.task)
            task_list_screen.add_task_to_list(self.task, self.list_selection)
            db.task_switch(self.task.uuid, self.list_selection)
            self.task.parent.update_list_positions()

        # Update task in the database
        db.update_task(self.task.uuid, self.task_name.text, self.notes.text, __projects__.selected_project.db_id)
        # Update task in the current session
        self.task.set_text(self.task_name.text)
        self.task.notes = self.notes.text
        self.task.project = __projects__.selected_project

        self.dismiss()

    def updated_list_flag(self, *args):
        self.list_changed_flag = True
        print("IT MOVED!")


class ProjectSelectionSection(BoxLayout):
    def open_project_screen(self):
        # send the task project or None
        self.task_screen.project_popup.open()
        self.task_screen.project_popup.set_project_list(__projects__())
        self.task_screen.project_popup.set_selected_project(__projects__.selected_project)

    def new_project_button_label_update(self, project):
        if project == __projects__.default:
            self.ids.new_project.text = "New"
        else:
            self.ids.new_project.text = "Edit"


class TaskListSelectionButton(ToggleButton):
    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)

__projects__ = ProjectList()
Factory.register('project_spinner_option', cls=ProjectSpinnerOption)