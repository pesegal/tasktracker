"""
    Tasklist that handles the ordering and displaying of objects.
"""

# Todo: Implement Reordering of tasks widgets.
# Todo: Implement creation and destruction of task widgets to support moving tasks between display windows.

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.lang import Builder
from src.task import Task
from src.db_interface import db

Builder.load_file('./src/taskcontainer.kv')


class ProjectSelector(Spinner):
    def __init__(self, **kwargs):
        super(ProjectSelector, self).__init__(**kwargs)
        self.text = 'No Project Selected'
        self.values = ['Project 1', 'Project 2', 'Project 3','Project 1', 'Project 2', 'Project 3','Project 1', 'Project 2', 'Project 3','Project 1', 'Project 2', 'Project 3']


class TaskScreen(Popup):
    pass


class TaskCreationScreen(TaskScreen):
    task_name = ObjectProperty(None)
    list_selection = NumericProperty(0)
    project_selection = NumericProperty(0)
    notes = ObjectProperty(None)

    # TODO: Get new task creation record to SQL

    def __init__(self, **kwargs):
        super(TaskCreationScreen, self).__init__(**kwargs)

    def create_task(self):
        t_list = self.parent.children[1].screen_controller.tasks
        print(self.task_name.text, self.list_selection, self.project_selection, self.notes.text)
        task_id = db.add_new_task(self.task_name.text, self.notes.text, self.list_selection, self.project_selection)
        task = Task(task_id, self.task_name.text, self.notes.text)
        t_list.add_task_to_list(task, self.list_selection)
        self.dismiss()


class TaskScrollContainer(ScrollView):
    def __init__(self, name='none', **kwargs):
        super(TaskScrollContainer, self).__init__(**kwargs)

        # Test to add something to display information!
        self.name = name
        self.task_list = TaskList(self.name)
        self.add_widget(self.task_list)


class TaskList(GridLayout):
    def __init__(self, name, **kwargs):
        super(TaskList, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 1
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))




