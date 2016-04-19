from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from src.taskview import TaskListScreen
from kivy.lang import Builder
from src.menubar import MenuBar

Builder.load_file('./src/screencontroller.kv')

class ScreenController(ScreenManager):
    def __init__(self, **kwargs):
        super(ScreenController, self).__init__(**kwargs)

        self.tasks = TaskListScreen(name='tasks')
        self.timer = TimerScreen(name='timer')
        self.stats = StatsScreen(name='stats')

        self.add_widget(self.tasks)
        self.add_widget(self.timer)
        self.add_widget(self.stats)


# TODO: Break this out into their own modules eventually.

class TimerScreen(Screen):
    pass


class StatsScreen(Screen):
    pass


class ScreenMenuAndDisplay(BoxLayout):
    def __init__(self, **kwargs):
        super(ScreenMenuAndDisplay, self).__init__(**kwargs)
        self.orientation = 'vertical'
        # This will list all the different sub-screens
        self.screen_controller = ScreenController()
        self.menu_bar = MenuBar()

        self.add_widget(self.menu_bar)
        self.add_widget(self.screen_controller)

