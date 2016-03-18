"""
    Author: Peter Segal
    Todo List Plus

"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout


class TaskListViewFull(BoxLayout):
    pass


class TaskListViewHalf(BoxLayout):
    pass


class TaskListViewSingle(BoxLayout):
    pass


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


class TaskApp(App):
    def build(self):
        return TaskListViewController()


if __name__ == '__main__':
    TaskApp().run()
