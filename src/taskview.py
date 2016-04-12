from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from src.taskcontainer import TaskScrollContainer
from kivy.lang import Builder

Builder.load_file('./src/taskview.kv')


class TaskListView(BoxLayout):
    """
       This class dynamically displays different scroll views based on how many
        widgets are supplied during construction this is used in conjunction with
        the task list view controller to provide changing views with window resize.
    """
    def __init__(self, widget, **kwargs):
        super(TaskListView, self).__init__(**kwargs)
        self.add_widget(widget)

    def view_change(self, widgets):
        child_list = tuple(self.children)
        for child in child_list:
            self.remove_widget(child)

        for widget in widgets:
            self.add_widget(widget)


class TaskListViewController(FloatLayout):
    def __init__(self, **kwargs):
        super(TaskListViewController, self).__init__(**kwargs)
        self.bind(size=self.screen_resize)
        self.today_list = TaskScrollContainer()
        self.tomorrow_list = TaskScrollContainer()
        self.future_list = TaskScrollContainer()

        self.current_display = TaskListView(self.today_list)
        self.add_widget(self.current_display)

        self.current_touch_pos = None

    def screen_resize(self, *args):
        if args[1][0] < 640:
            self.current_display.view_change([self.today_list])
        elif 640 < args[1][0] < 960:
            self.current_display.view_change([self.today_list, self.tomorrow_list])
        elif args[1][0] > 960:
            self.current_display.view_change([self.today_list, self.tomorrow_list, self.future_list])

    def click_drag_reposition(self, task, size, position):
        task.parent.remove_widget(task)
        self.add_widget(task)
        task.pos = position
        task.size_hint_x = None
        task.size = size

    def check_children(self, touch_pos):
        """
        This function returns the task list widget and the task widget the touch position releases on.
        :param touch_pos:
        :return: TaskList Widget, Task Object
        """
        # TODO Will need to add a check in case it's not a scroll view.
        t_list = None
        task = None

        for child in self.children:
            if not child.collide_point(*touch_pos):
                continue
            for c in child.children:
                if c.collide_point(*touch_pos):
                    t_list = c.task_list
            if not t_list:
                continue
            for tasks in t_list.children:
                if tasks.collide_point(*tasks.to_widget(*touch_pos)):
                    task = tasks
        return t_list, task