""" The Timer module contains all of the controller logic for the timer In the system.
"""

from copy import copy

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton, ToggleButtonBehavior
from kivy.properties import NumericProperty, ObjectProperty, ListProperty, BooleanProperty, StringProperty

from tasktracker.themes import themes
from tasktracker.themes.themes import Themeable
from tasktracker.task.task import Task

# TODO: Break these out to the settings module
POMO_TIME = 25 * 60
SHORT_BREAK = 5 * 60
LONG_BREAK = 15 * 60

# TODO: Create timer selection logic for buttons.
# TODO: Create bool flag to switch between start and stop functionality.

# Types of task actions
# 1 - unknown
# 2 - Pomodoro
# 3 - Pause
# 4 - Short Break
# 5 - Long Break
# 6 - Stopwatch


class TimerScreen(Screen, Themeable):
    """ TimerScreen Object contains all of the  control logic relating to the timer screen.
    The layout information of the Timer Screen is located in the 'timer.kv' file in the layouts
    directory.
    """
    # Theme Properties
    text_color = ListProperty(themes.THEME_CONTROLLER.text)

    # Functional Properties
    _clock_event = ObjectProperty()
    timer_active = BooleanProperty(False)
    timer_type_selection = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.current_time = POMO_TIME
        self._timer_display_update()


    def theme_update(self):
        self.text_color = self.theme.text
        self.text_color[3] = .88

    def switch_timer_type(self, selected):
        self.timer_type_selection = selected
        if not self.timer_active:
            print("Changing Timer Types")
            if selected == 0:
                self.current_time = POMO_TIME
            elif selected == 1:
                self.current_time = SHORT_BREAK
            elif selected == 2:
                self.current_time = LONG_BREAK
            elif selected == 3:
                self.current_time = 0
        self._timer_display_update()

    def _timer_display_update(self):
        minutes, seconds = divmod(self.current_time, 60)
        self.ids.timer.text = ('[b]%02d[/b]:%02d' % (int(minutes), int(seconds)))

    def timer_reset(self):
        self.timer_active = False
        Clock.unschedule(self._clock_event)
        self.ids.start_pause_button.text = 'Start'
        self.switch_timer_type(self.timer_type_selection)

    def start_pause_trigger(self):
        if self.timer_type_selection == 3:
            timer_function = self.update
        else:
            timer_function = self.count_down

        if self.timer_active:
            self.ids.start_pause_button.text = 'Start'
            Clock.unschedule(self._clock_event)
            self.timer_active = False
        else:
            self._clock_event = Clock.schedule_interval(timer_function, 0.016)
            self.ids.start_pause_button.text = 'Pause'
            self.timer_active = True

    def update(self, nap):
        self.current_time += nap
        self._timer_display_update()

    def count_down(self, nap):
        self.current_time -= nap
        minutes, seconds = divmod(self.current_time, 60)
        if self.current_time <= 0:
            self.count_down_alert()
            Clock.unschedule(self._clock_event)
            self.current_time = 0
        else:
            self.ids.timer.text = ('[b]%02d[/b]:%02d' % (int(minutes), int(seconds)))

    def count_down_alert(self):
        # Use this function to trigger notifications and other logic when the
        # count down timer is finished.
        print("FINISHED")
        # TODO: DATABASE STUFF!


class TimerTaskDisplayManager(BoxLayout):
    """ This object acts as an interface for the selected task widget display on the timer screen.
    when no project is selected this widget will show the default view of a button that allows
    the user to select a project to work on.
    """
    def __init__(self, **kwargs):
        super(TimerTaskDisplayManager, self).__init__(**kwargs)
        self.default = NoProjectSelectedButton()
        self.selected = self.default
        self.add_widget(self.selected)

    def load_task(self, task):
        self.clear_widgets()
        # TODO: Add in parts to write to the database when a task is switched in mid session.
        self.selected = TaskDisplay(task.uuid, task.tasktext.text, task.notes, task.project.db_id)
        self.add_widget(self.selected)
        print(self.selected.uuid)
        print(self.selected.tasktext.text)

    def _reset_default_task(self):
        self.clear_widgets()
        self.add_widget(self.default)


class NoProjectSelectedButton(Button):
    background = StringProperty(themes.NO_TASK_TEXTURE)

    def __init__(self, **kwargs):
        super(NoProjectSelectedButton, self).__init__(**kwargs)
        self.text = 'Select a project!'

    def theme_update(self):
        pass


class TaskDisplay(Task):
    """ TaskDisplay inherits all the display functionality of the task widget
        without the control functionality.
    """
    def __init__(self, *args, **kwargs):
        super(TaskDisplay, self).__init__(*args, **kwargs)

    def on_press(self):
        pass

    def on_touch_down(self, touch):
        pass

    def on_touch_move(self, touch):
        pass

    def on_release(self):
        pass


class TimerSettingsButton(ToggleButton, Themeable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        pass

    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)