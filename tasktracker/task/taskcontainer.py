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
        t_list = self.parent.children[1].screen_controller.tasks
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
        self.load_task_data(task.uuid)

    def load_task_data(self, task_id):
        task_data = db.load_task_data(task_id)
        print(task_data)

    def update_task(self):
        pass


class TaskScrollContainer(ScrollView):
    def __init__(self, list_id, name='none', **kwargs):
        super(TaskScrollContainer, self).__init__(**kwargs)

        # Test to add something to display information!
        self.list_id = list_id
        self.name = name
        self.task_list = TaskList(self.list_id)
        self.add_widget(self.task_list)


class TaskList(GridLayout):
    def __init__(self, list_id, **kwargs):
        super(TaskList, self).__init__(**kwargs)
        self.list_id = list_id
        self.cols = 1
        self.spacing = 1
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

    def update_list_positions(self):
        for index, child in enumerate(self.children):
            db.update_task_list_index(index, child.uuid)






