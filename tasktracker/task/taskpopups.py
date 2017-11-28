"""
    Contains all controller logic for the Task Creation/Edit Screens and Project Edit Screens.
"""
import weakref
from kivy.factory import Factory
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, ListProperty, StringProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.utils import get_color_from_hex, get_hex_from_color

from tasktracker.database.db_interface import DB
from tasktracker.settings.settingscontroller import PROJECT_COLORS, APP_CONTROL, DataContainer
from tasktracker.task.task import Task
from tasktracker.themes.themes import Themeable
from tasktracker.themes import themes


class Project:
    """ Project class is a data structure that contains project data.
    """
    def __init__(self, id, creation, deletion, name, color, color_name):
        self._observers = list()
        self.db_id = id
        self.name = name
        self.creation_date = creation
        self.deletion_date = deletion
        self._color = color
        self.color_name = color_name

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._flush()
        for observer in self._observers:
            if hasattr(observer(), 'update_project_color'):
                observer().update_project_color(get_color_from_hex(self._color))

    def register(self, observer):
        self._observers.append(weakref.ref(observer))

    def _flush(self):
        to_remove = []

        for ref in self._observers:
            if ref() is None:
                to_remove.append(ref)

        for item in to_remove:
            self._observers.remove(item)


class ProjectList(DataContainer):
    """ProjectList Class is a global container that is used to load and track
    modification to project objects.
    """

    def __init__(self):
        super(ProjectList, self).__init__()
        self.project_list = list()
        self.load_all_projects()

    def __call__(self):
        return self.project_list

    def clear_data(self):
        self.project_list = list()

    def load_data(self):
        self.load_all_projects()

    def load_all_projects(self):
        DB.load_all_projects(self._loaded_all_projects)

    def _loaded_all_projects(self, projects, dt):
        self.project_list = list()
        for project in projects:
            print(project)
            self.project_list.append(Project(*project))


            # TODO: DO THESE TWO LINES CAUSE AN ISSUE?
        self.default = self.project_list[0]
        self.selected_project = self.default

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

# SPINNER WIDGET WIDGETS!


class ThemedDropdown(DropDown, Themeable):
    bg_texture = StringProperty(themes.NO_BEV_CORNERS)
    bg_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = self.theme.list_bg
        self.container.spacing = 3

    def theme_update(self):
        self.bg_color = self.theme.list_bg


class ProjectSpinnerOption(SpinnerOption, Themeable):
    """ Extending the SpinnerOption widget allows for customization of the drawing of the widget.
    """
    button_texture = StringProperty(themes.NO_BEV_CORNERS)
    project_texture = StringProperty(themes.NO_BEV_CORNERS)
    button_color = ListProperty([0, 0, 0, 0])
    text_color = ListProperty()
    selected_color = ListProperty()
    project_color = ListProperty([0, 0, 0, 0])  # Init to a blank to stop error from displaying with the shader
    project_object = ObjectProperty()

    def __init__(self, **kwargs):
        super(ProjectSpinnerOption, self).__init__(**kwargs)
        if self.text != 'No Project':
            self.project_object = PROJECT_LIST.return_project_by_name(self.text)
            self.project_object.register(self)
            self.set_project_color(get_color_from_hex(self.project_object.color))
        else:
            # kivy default: [47 / 255., 167 / 255., 212 / 255., 1.]
            self.set_project_color(self.theme.selected)

        self.text_color = self.theme.text
        self.text_color[3] = .9
        self.button_color = self.theme.background
        self.selected_color = self.theme.selected

    def theme_update(self):
        self.text_color = self.theme.text
        self.text_color[3] = .9
        self.button_color = self.theme.background
        self.selected_color = self.theme.selected

    def set_project_color(self, color):
        self.project_color = color

    def update_project_color(self, value):
        self.project_color = value

    def on_state(self, widget, value):
        if self.state == 'down':
            self.button_color = self.theme.selected
        else:
            self.button_color = self.theme.background


class ProjectSelector(Spinner, Themeable):
    """ Project Selector contains is the controller functionality for the spinner
    widget that is on the main task screen. The view logic is contained inside
    the taskcontainer.kv layout file.
    """
    button_texture = StringProperty(themes.ALL_BEV_CORNERS)
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    text_color = ListProperty()
    button_color = ListProperty()
    shadow_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = list()
        self.bind(text=self.project_change)
        self.dropdown_cls = ThemedDropdown
        self.option_cls = 'project_spinner_option'

        # Theme Stuff
        self.text_color = self.theme.text
        self.text_color[3] = .8
        self.button_color = self.theme.tasks
        self.shadow_color = themes.SHADOW_COLOR

    def theme_update(self):
        self.text_color = self.theme.text
        self.button_color = self.theme.tasks

    def set_project(self, project):
        self.text = project.name

    def load_projects(self, projects):
        for project in projects:
            self.values.append(project.name)

    def project_change(self, spinner, text):
        PROJECT_LIST.change_project(text)
        self.parent.new_project_button_label_update(PROJECT_LIST.selected_project)

    def set_drop_down_height(self, height, offset):
        self.dropdown_cls.max_height = height - offset

    def on_state(self, widget, value):
        if self.state == 'down':
            self.button_color = self.theme.selected
        else:
            self.button_color = self.theme.tasks


class ProjectPopupSelector(ProjectSelector):
    """ ProjectPopupSelector contains the controller logic for the project selection spinner widget
        that is inside the ProjectPopup window.
    """
    popup = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ProjectPopupSelector, self).__init__(**kwargs)
        self.set_project(PROJECT_LIST.selected_project)
        self.load_projects(PROJECT_LIST())
        self.height_offset = 150

    def project_change(self, spinner, text):
        PROJECT_LIST.change_project(text)
        if self.popup:
            self.popup.set_selected_project(PROJECT_LIST.selected_project)


class ProjectSelectionSection(BoxLayout):
    """This object contains the projects spinner on the task creation and edit screen and controller
    functionality for the new/edit projects button!
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def open_project_screen(self):
        # send the task project or None
        self.task_screen.project_popup.open()
        self.task_screen.project_popup.set_project_list(PROJECT_LIST())
        self.task_screen.project_popup.set_selected_project(PROJECT_LIST.selected_project)

    def new_project_button_label_update(self, project):
        if project == PROJECT_LIST.default:
            self.ids.new_project.text = "New"
        else:
            self.ids.new_project.text = "Edit"


# PROJECT POPUP CONTROLLERS

class ProjectPopup(Popup, Themeable):
    """ ProjectPopup is the controller for most of the logic for the project selection and editing.
    popup. This contains the function to trigger creating and updating project records in the database.
    """
    edit = BooleanProperty(False)

    # Theme Properties
    bg_shade_color = ListProperty()
    bg_popup_color = ListProperty()
    label_color = ListProperty()
    transparent_texture = StringProperty(themes.TRANSPARENT_TEXTURE)
    popup_texture = StringProperty(themes.NO_BEV_CORNERS)
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)

    def __init__(self, **kwargs):
        super(ProjectPopup, self).__init__(**kwargs)
        # self.project = project
        self.default_color = self.theme.selected
        self.selected_project = PROJECT_LIST.default
        self.project_list = None
        self.ids.color_selector.load_color_buttons()
        self.current_selected_color = None
        self.current_selected_color_name = None
        self.bind(edit=self.create_update_button_update)

        # Theme Initialization
        self.bg_shade_color = self.theme.list_bg
        self.bg_shade_color[3] = .7
        self.bg_popup_color = self.theme.list_bg
        self.label_color = self.theme.text

    def theme_update(self):
        self.bg_shade_color = self.theme.list_bg
        self.bg_shade_color[3] = .7
        self.bg_popup_color = self.theme.list_bg
        self.label_color = self.theme.text

    def set_project_list(self, projects):
        self.project_list = projects

    def set_selected_project(self, project):
        self.ids.popup_selector.set_project(project)
        self.selected_project = project
        self.current_selected_color = self.selected_project.color
        self.current_selected_color_name = self.selected_project.color_name

        if self.selected_project == PROJECT_LIST.default:
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
            DB.update_project(self.selected_project)
        else:
            # Checks for field completeness and creates project.
            name, color = self.ids.project_title.text, self.current_selected_color
            color_name = self.current_selected_color_name
            if name != "" and color:
                DB.new_project(name, color, color_name, self._new_project_finished)
        self.dismiss()

    def _new_project_finished(self, pid, td):
        PROJECT_LIST.load_all_projects()
        PROJECT_LIST.change_project_by_id(pid[0])


class ColorSelectionWindow(GridLayout):
    """ ColorSelectionWindow is the controller for the multiple diffrent colors one can select for a project.
    """
    popup = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ColorSelectionWindow, self).__init__(**kwargs)

    def load_color_buttons(self):
        self.cols = 11
        for name, color in PROJECT_COLORS.get_name_and_hex_values():
            self.add_widget(ColorSelectionButton(name, color))

    def find_and_select_button(self, hex):
        for child in self.children:
            if child.hex == hex:
                child.state = 'down'
                self.popup.update_project_color(child.name, child.background_color)


class ColorSelectionButton(ToggleButton, Themeable):
    """ Contains controller functionality for the buttons that show color selection.
    """
    button_texture = StringProperty(themes.NO_BEV_CORNERS)

    def __init__(self, name, color, **kwargs):
        super(ColorSelectionButton, self).__init__(**kwargs)
        self.name = name
        self.group = 'color_selections'
        self.hex = color
        self.background_normal = ''
        self.background_color = get_color_from_hex(color)

    def theme_update(self):
        pass

    def on_press(self):
        self.parent.popup.current_selected_color = self.hex
        self.parent.popup.update_project_color(self.name, self.background_color)


# MAIN POPUP CONTROLLERS

class TaskScreen(Popup, Themeable):
    """ This is the parent class for both the new task screen and the task creation screen.
    It contains controller logic that is shared between both types of popups.
    """
    # Functional Properties
    task_name = ObjectProperty(None)
    list_selection = NumericProperty(0)
    notes = ObjectProperty(None)
    project_popup = ObjectProperty(None)
    project_open = BooleanProperty(False)
    selector_open = BooleanProperty(False)

    # Theme Properties
    bg_shade_color = ListProperty()
    bg_popup_color = ListProperty()
    label_color = ListProperty()
    transparent_texture = StringProperty(themes.TRANSPARENT_TEXTURE)
    popup_texture = StringProperty(themes.NO_BEV_CORNERS)
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)

    def __init__(self, **kwargs):
        super(TaskScreen, self).__init__(**kwargs)
        self.project_popup = ProjectPopup()
        self.ids.project_selection_section.ids.selector.set_project(PROJECT_LIST.default)
        self.ids.project_selection_section.ids.selector.load_projects(PROJECT_LIST())
        self.bind(height=self._set_max_height)
        self._set_max_height(self, self.height)
        self.project_popup.bind(on_open=self._project_popup_opened)
        self.project_popup.bind(on_dismiss=self.project_updated)

        # Theme Initialization
        self.bg_shade_color = self.theme.list_bg
        self.bg_shade_color[3] = .7
        self.bg_popup_color = self.theme.list_bg
        self.label_color = self.theme.text
        self.separator_color = self.theme.selected

    def theme_update(self):
        self.bg_shade_color = self.theme.list_bg
        self.bg_shade_color[3] = .7
        self.bg_popup_color = self.theme.list_bg
        self.label_color = self.theme.text

    def project_updated(self, popup):
        self.project_open = False
        self._set_max_height(self, self.height)
        self.ids.project_selection_section.ids.selector.set_project(PROJECT_LIST.selected_project)

    def _project_popup_opened(self, popup):
        self.project_open = True
        self._set_max_height(self, self.height)

    def _set_max_height(self, this, height):
        if self.project_open:
            offset = 145  # Drop down stops at bottom of text input
        else:
            offset = 215  # Drop down stops at bottom of color buttons
        self.ids.project_selection_section.ids.selector.set_drop_down_height(height, offset)


class TaskCreationScreen(TaskScreen):
    """ TaskCreationScreen is shown when a clicks the create new task button. View logic is contained
    in taskcontainer.kv.
    """
    def __init__(self, **kwargs):
        super(TaskCreationScreen, self).__init__(**kwargs)

    def create_task(self, selector_open):
        if not selector_open:
            t_list = APP_CONTROL.task_list_screen
            new_task_index = t_list.get_list_length(self.list_selection)
            DB.add_new_task(self.task_name.text, self.notes.text, self.list_selection,
                            new_task_index, PROJECT_LIST.selected_project.db_id,
                            self._task_creation_finalization)
            self.dismiss()

    def _task_creation_finalization(self, task_id):
        task = Task(task_id, self.task_name.text, self.notes.text, self.list_selection)
        APP_CONTROL.task_list_screen.add_task_to_list(task, self.list_selection)
        task.project = PROJECT_LIST.selected_project


class TaskEditScreen(TaskScreen):
    """ TaskEditScreen contains controller logic for the editable task screen version of the code.
    """
    def __init__(self, task, **kwargs):
        super(TaskEditScreen, self).__init__(**kwargs)
        self.list_changed_flag = False
        DB.load_task_data(task.uuid, self._load_task_data)
        self.task = task
        # Todo: Look into setting the separator bar to the selected projects color!

    def _load_task_data(self, task_data, td):
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
        PROJECT_LIST.selected_project = PROJECT_LIST.return_project_by_id(task_data[3])
        self.ids.project_selection_section.ids.selector.set_project(PROJECT_LIST.selected_project)

        self.bind(list_selection=self.updated_list_flag)

    def update_task(self, selector_open):
        if not selector_open:
            if self.list_changed_flag:
                task_list_screen = APP_CONTROL.task_list_screen
                self.task.parent.remove_widget(self.task)
                task_list_screen.add_task_to_list(self.task, self.list_selection)
                DB.task_switch(self.task.uuid, self.list_selection)
                self.task.parent.update_list_positions()

            # Update task in the database
            DB.update_task(self.task.uuid, self.task_name.text, self.notes.text, PROJECT_LIST.selected_project.db_id)
            # Update task in the current session
            self.task.set_text(self.task_name.text)
            self.task.notes = self.notes.text
            self.task.project = PROJECT_LIST.selected_project

            self.dismiss()

    def updated_list_flag(self, *args):
        self.list_changed_flag = True


class TaskListSelectionButton(ToggleButton, Themeable):
    button_texture = StringProperty(themes.ALL_BEV_CORNERS)
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    text_color = ListProperty()
    button_color = ListProperty()
    shadow_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Theme Init Stuff
        self.button_color = self.theme.tasks
        self.text_color = self.theme.text
        self.text_color[3] = .8
        self.shadow_color = themes.SHADOW_COLOR

    def theme_update(self):
        self.button_color = self.theme.tasks
        self.text_color = self.theme.text
        self.text_color[3] = .8
        self.on_state(self, 0)

    def on_state(self, widget, value):
        if self.state == 'down':
            self.button_color = self.theme.selected
        else:
            self.button_color = self.theme.tasks

    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)


# THEMED EXTRAS

class ThemedButton(Button, Themeable):
    button_texture = StringProperty(themes.ALL_BEV_CORNERS)
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    text_color = ListProperty()
    button_color = ListProperty()
    shadow_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Theme Init Stuff
        self.button_color = self.theme.tasks
        self.text_color = self.theme.text
        self.text_color[3] = .8
        self.shadow_color = themes.SHADOW_COLOR

    def theme_update(self):
        self.button_color = self.theme.tasks
        self.text_color = self.theme.text
        self.text_color[3] = .8
        self.on_state(self, 0)

    def on_state(self, widget, value):
        if self.state == 'down':
            self.button_color = self.theme.selected
        else:
            self.button_color = self.theme.tasks


class ThemedTextInput(TextInput, Themeable):
    input_texture = StringProperty(themes.ALL_BEV_CORNERS)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = self.theme.background
        self.cursor_color = self.theme.selected
        # self.hint_text_color = self.theme.selected
        self.foreground_color = self.theme.text

    def theme_update(self):
        self.background_color = self.theme.background


PROJECT_LIST = ProjectList()
Factory.register('project_spinner_option', cls=ProjectSpinnerOption)
