"""
    Author: Peter Segal
    Todo List Plus

"""
from kivy.app import App
from src.screencontroller import ScreenMenuAndDisplay

class TaskApp(App):
    def build(self):
        self.title = 'TaskTracker++'
        return ScreenMenuAndDisplay()

if __name__ == '__main__':
    TaskApp().run()
