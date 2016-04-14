"""
    Author: Peter Segal
    Todo List Plus

"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from src.taskview import TaskListViewController
from src.menubar import MenuBar


class ScreenController(BoxLayout):
    def __init__(self, **kwargs):
        super(ScreenController, self).__init__(**kwargs)
        self.orientation = 'vertical'
        # This will list all the different sub-screens
        self.main_screen = TaskListViewController()
        self.menu_bar = MenuBar()

        self.add_widget(self.menu_bar)
        self.add_widget(self.main_screen)


class TaskApp(App):
    def build(self):
        return ScreenController()


if __name__ == '__main__':
    TaskApp().run()
