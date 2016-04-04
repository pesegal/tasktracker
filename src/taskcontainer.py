"""
    Tasklist that handles the ordering and displaying of objects.
"""

# Todo: Implement Reordering of tasks widgets.
# Todo: Implement creation and destruction of task widgets to support moving tasks between display windows.

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from src.task import Task


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
            self.add_widget(task)

    def add_task(self):
        self.add_widget(Task(text="This is a test"))

    def switch_positions(self, task):
        wid_to_switch = None
        for child in self.children:
            print(child)
            if child.collide_widget(task) and child is not task:  # task collides with itself.
                print('FOUND!!!!')
                wid_to_switch = child

        print(wid_to_switch)

        if wid_to_switch:
            wid_index = self.children.index(wid_to_switch)
            task_index = self.children.index(task)

            self.children[wid_index], self.children[task_index] = self.children[task_index], self.children[wid_index]
        else:
            print("No collision detected")




