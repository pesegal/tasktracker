""" The Timer module contains all of the controller logic for the timer In the system.
"""


from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton, ToggleButtonBehavior
from kivy.properties import NumericProperty, ObjectProperty

from tasktracker.themes.themes import Themeable

# TODO: Break these out to the settings module
POMOTIME = 25
SHORT_BREAK = 5 * 60
LONG_BREAK = 15


class TimerScreen(Screen, Themeable):
    current_time = NumericProperty(0)
    _clock_event = ObjectProperty()
    timer_type_selection = NumericProperty(0)

    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(self.timer_type_selection, self.do_stuff)

    def do_stuff(self):
        print(self.timer_type_selection)

    def on_start(self):
        self.current_time = SHORT_BREAK
        # Check to make sure timer works at correct speed.
        self._clock_event = Clock.schedule_interval(self.count_down, 0.016)

    def update(self, nap):
        self.current_time += nap
        print(self.current_time)

        minutes, seconds = divmod(self.current_time, 60)

        self.ids.timer.text = ('%02d:%02d' % (int(minutes), int(seconds)))

    def count_down(self, nap):
        self.current_time -= nap
        minutes, seconds = divmod(self.current_time, 60)
        if self.current_time <= 0:
            print("FINISHED")
            Clock.unschedule(self._clock_event)
        else:
            self.ids.timer.text = ('[b]%02d[/b]:%02d' % (int(minutes), int(seconds)))

    def update_time(self, nap):
        pass

    def theme_update(self):
        pass


class TimerSettingsButton(ToggleButton, Themeable):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        pass

    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)