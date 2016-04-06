"""
    Author: Peter Segal
    Todo List Plus

"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from src.taskcontainer import TaskScrollContainer

Builder.load_file('./src/taskcontainer.kv')
Builder.load_file('./src/task.kv')


class TaskListViewFull(BoxLayout):
    pass


class TaskListViewHalf(BoxLayout):
    pass


class TaskListViewSingle(BoxLayout):
    pass

# Todo: Each TaskScrollContainer should be a named widget so when redrawing it saves the internal context
class TaskListViewController(Widget):
    def __init__(self, **kwargs):
        super(TaskListViewController, self).__init__(**kwargs)
        self.bind(size=self.screen_resize)
        self.full_view = TaskListViewFull()
        self.half_view = TaskListViewHalf()
        self.sing_view = TaskListViewSingle()


        self.current_display = self.sing_view

    def screen_resize(self, *args):
        def swap_display(display):
            self.remove_widget(self.current_display)
            self.current_display = display
            self.add_widget(self.current_display)
            self.current_display.size = self.size

        if args[1][0] < 640:
            swap_display(self.sing_view)
        elif 640 < args[1][0] < 960:
            swap_display(self.half_view)
        elif args[1][0] > 960:
            swap_display(self.full_view)

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
