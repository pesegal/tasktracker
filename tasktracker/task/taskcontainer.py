"""
    Tasklist that handles the ordering and displaying of objects.
"""

# Todo: Implement Reordering of tasks widgets.
# Todo: Implement creation and destruction of task widgets to support moving tasks between display windows.

from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner

from tasktracker.database.db_interface import db
from tasktracker.task.task import Task


class ProjectSelector(Spinner):
    def __init__(self, **kwargs):
        super(ProjectSelector, self).__init__(**kwargs)
        self.text = 'No Project Selected'
        self.values = ['Project 1', 'Project 2', 'Project 3', 'Project 1', 'Project 2', 'Project 3','Project 1', 'Project 2', 'Project 3','Project 1', 'Project 2', 'Project 3']


class TaskScreen(Popup):
    task_name = ObjectProperty(None)
    list_selection = NumericProperty(0)
    project_selection = NumericProperty(0)
    notes = ObjectProperty(None)


class TaskCreationScreen(TaskScreen):
    def __init__(self, **kwargs):
        super(TaskCreationScreen, self).__init__(**kwargs)

    def create_task(self):
        print(self.parent)
        t_list = self.parent.children[1].screen_controller.tasks  # TODO FIX THIS LINE!
        new_task_index = t_list.get_list_length(self.list_selection)
        print(self.list_selection, self.project_selection)
        task_id = db.add_new_task(self.task_name.text, self.notes.text, self.list_selection,
                                  new_task_index, self.project_selection)
        task = Task(1, self.task_name.text, self.notes.text)
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







