from kivy.uix.screenmanager import Screen
from kivy.garden.timeline import Timeline, TimeTick, selected_time_ticks
from kivy.properties import ObjectProperty
from kivy.metrics import dp

from datetime import datetime, timezone

from tasktracker.settings import APP_CONTROL
from tasktracker.themes import themes


class TaskTimeLine(Timeline):
    testview = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_time = datetime.now(timezone.utc)

    def redraw_(self, *args):
        super().redraw_(*args)
        print(self.time_0, self.time_1)

    def _print_stuff(self, *args):
        print(*args)




class StatsScreen(Screen):  # TODO: Break this out into it's own module eventually.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        time_ticks = [TimeTick(mode=TimeTick.mode.options[i], valign='line_top') for i in [0, 3, 5, 7, 9, 10, 12, 14, 15]]

        test_timeline = TaskTimeLine(orientation='horizontal', ticks=time_ticks, line_width=1.)

        test_timeline.cover_background = False

        self.add_widget(test_timeline)








