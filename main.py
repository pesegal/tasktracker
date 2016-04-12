"""
    Author: Peter Segal
    Todo List Plus

"""
from kivy.app import App
from src.taskview import TaskListViewController



class TaskApp(App):
    def build(self):
        return TaskListViewController()


if __name__ == '__main__':
    TaskApp().run()
