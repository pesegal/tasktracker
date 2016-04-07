"""
    Author: Peter Segal
    Todo List Plus

"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from src.taskcontainer import TaskScrollContainer

Builder.load_file('./src/taskcontainer.kv')
Builder.load_file('./src/task.kv')


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

    def screen_resize(self, *args):
        if args[1][0] < 640:
            self.current_display.view_change([self.today_list])
        elif 640 < args[1][0] < 960:
            self.current_display.view_change([self.today_list, self.tomorrow_list])
        elif args[1][0] > 960:
            self.current_display.view_change([self.today_list, self.tomorrow_list, self.future_list])

    def click_drag_reposition(self, task):
        print('ADDING TASK')
        task_pos = task.x
        print(task_pos)
        task.parent.remove_widget(task)
        self.add_widget(task)
        print(task.pos)
        #task.pos = task_pos

    def check_children(self, touch_pos):
        # TODO Will need to add a check in case it's not a scroll view.
        for child in self.children:
            for c in child.children:
                if c.collide_point(*touch_pos):
                    return c.task_list

class TaskApp(App):
    def build(self):
        return TaskListViewController()


if __name__ == '__main__':
    TaskApp().run()
