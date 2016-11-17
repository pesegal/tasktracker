from kivy.uix.screenmanager import Screen
from kivy.garden.timeline import Timeline, TimeTick, selected_time_ticks
from kivy.metrics import dp

from tasktracker.settings import APP_CONTROL
from tasktracker.themes import themes

class StatsScreen(Screen):  # TODO: Break this out into it's own module eventually.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        time_ticks = [TimeTick(mode=TimeTick.mode.options[i], valign='line_top') for i in [0, 3, 5, 7, 9, 10, 12, 14, 15]]

        test_timeline = Timeline(orientation='horizontal', ticks=time_ticks, line_width=1.)

        test_timeline.cover_background = False

        self.add_widget(test_timeline)






