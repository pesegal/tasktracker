from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty
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
    screen_size = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ScreenMenuAndDisplay, self).__init__(**kwargs)
        self.orientation = 'vertical'
        # This will list all the different sub-screens
        self.bind(size=self.screen_state)
        self.screen_controller = ScreenController()
        self.menu_bar = MenuBar()

        self.bind(screen_size=self.print_change)

        self.add_widget(self.menu_bar)
        self.add_widget(self.screen_controller)

    def screen_state(self, *args):
        if args[1][0] < 640:
            self.screen_size = 0
        elif 640 < args[1][0] < 960:
            self.screen_size = 1
        elif 960 < args[1][0] < 1280:
            self.screen_size = 2
        elif 1280 < args[1][0]:
            self.screen_size = 3

    def print_change(self, *args):
        print(self.screen_size, "ARGS: ", args)




