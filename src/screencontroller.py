from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty
from src.taskview import TaskListScreen
from kivy.lang import Builder
from src.menubar import MenuBar
from src.broadcast import BroadcastMixin


Builder.load_file('./src/screencontroller.kv')


class ScreenController(ScreenManager, BroadcastMixin):
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


class ScreenMenuAndDisplay(BoxLayout, BroadcastMixin):
    screen_size = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ScreenMenuAndDisplay, self).__init__(**kwargs)
        self.orientation = 'vertical'
        # This will list all the different sub-screens
        self.bind(size=self.screen_width_state)
        self.screen_controller = ScreenController()
        self.menu_bar = MenuBar()

        # This is where you transmit
        self.bind(screen_size=self.broadcast_window_resize)

        self.add_widget(self.menu_bar)
        self.add_widget(self.screen_controller)

    def screen_width_state(self, *args):
        if args[1][0] < 360:  # Small width screens where text needs to be icons
            self.screen_size = 0
        elif 360 < args[1][0] < 640:  # Single list
            self.screen_size = 1
        elif 640 < args[1][0] < 960:
            self.screen_size = 2
        elif 960 < args[1][0] < 1280:
            self.screen_size = 3
        elif 1280 < args[1][0]:
            self.screen_size = 4

    def broadcast_window_resize(self, *args):
        # print(self.screen_size, "ARGS: ", args)
        self.broadcast_child('width_state_change', width_state=self.screen_size)








