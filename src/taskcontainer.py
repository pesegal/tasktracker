"""
    Tasklist that handles the ordering and displaying of objects.
"""

# Todo: Implement Reordering of tasks widgets.
# Todo: Implement creation and destruction of task widgets to support moving tasks between display windows.

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.lang import Builder
from src.task import Task

Builder.load_file('./src/taskcontainer.kv')


class TaskCreationScreen(Popup):
    pass  #: TODO: Add Task creation functionality


class TaskScrollContainer(ScrollView):
    def __init__(self, **kwargs):
        super(TaskScrollContainer, self).__init__(**kwargs)

        # Test to add something to display information!
        self.task_list = TaskList()
        self.add_widget(self.task_list)


class TaskList(GridLayout):
    def __init__(self, **kwargs):
        super(TaskList, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 1
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

        for i in range(5):
            task = Task(text=str(i))
            task.text = str(task.uid)
            self.add_widget(task)

    def add_task(self):
        self.add_widget(Task(text="Created"))




