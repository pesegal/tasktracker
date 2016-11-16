from kivy.uix.screenmanager import Screen
from kivy.garden.timeline import Timeline, TimeTick, selected_time_ticks
from kivy.metrics import dp


class StatsScreen(Screen):  # TODO: Break this out into it's own module eventually.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(        Timeline(backward=True,
                 orientation='horizontal',
                 ticks=(selected_time_ticks() +
                         [TimeTick(valign='top',
                                   mode='12 hours'),
                          TimeTick(valign='line_bottom',
                                   mode='2 hours')]),
                 line_offset=dp(130)
                 ))






