""" The Timer module contains all of the controller logic for the timer In the system.
"""


from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton, ToggleButtonBehavior
from kivy.properties import NumericProperty, ObjectProperty, ListProperty, BooleanProperty

from tasktracker.themes import themes
from tasktracker.themes.themes import Themeable

# TODO: Break these out to the settings module
POMOTIME = 25
SHORT_BREAK = 5 * 60
LONG_BREAK = 15

# TODO: Create timer selection logic for buttons.
# TODO: Create bool flag to switch between start and stop functionality.


class TimerScreen(Screen, Themeable):
    """ TimerScreen Object contains all of the  control logic relating to the timer screen.
    The layout information of the Timer Screen is located in the 'timer.kv' file in the layouts
    directory.
    """
    # Theme Properties
    text_color = ListProperty(themes.THEME_CONTROLLER.text)

    # Functional Properties
    current_time = NumericProperty(SHORT_BREAK)
    _clock_event = ObjectProperty()
    timer_active = BooleanProperty(False)

    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_type_selection = 0

    def theme_update(self):
        self.text_color = self.theme.text
        self.text_color[3] = .88

    def switch_timer_type(self, selected):
        self.timer_type_selection = selected
        print("Timer Type Selected: ", self.timer_type_selection)
        # TODO: Add logic here to display the selected time on the timer label.

    def start_pause_trigger(self):
        print(self.current_time)
        # TODO: Need to call the function to make sure that default times are displayed before starting timer.
        if self.timer_active:
            self.ids.start_pause_button.text = 'Start'
            Clock.unschedule(self._clock_event)
            self.timer_active = False
        else:
            self._clock_event = Clock.schedule_interval(self.count_down, 0.016)
            self.ids.start_pause_button.text = 'Pause'
            self.timer_active = True

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


class TimerSettingsButton(ToggleButton, Themeable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        pass

    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)