""" The Timer module contains all of the controller logic for the timer In the system.
"""

from datetime import datetime

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton, ToggleButtonBehavior
from kivy.properties import NumericProperty, ObjectProperty, ListProperty, BooleanProperty, StringProperty

from tasktracker.themes import themes
from tasktracker.themes.themes import Themeable
from tasktracker.task.task import Task
from tasktracker.database.db_interface import DB

# TODO: Break these out to the settings module

POMO_TIME = 25 * 60
SHORT_BREAK = 5 * 60
LONG_BREAK = 15 * 60

# Types of task actions
# 1 - unknown
# 2 - Pomodoro
# 3 - Pause
# 4 - Short Break
# 5 - Long Break
# 6 - Stopwatch


class TaskAction:
    def __init__(self, task_id, action_type, start_time):
        self.task_id = task_id
        self.type = action_type
        self.start_time = start_time
        self.finish_time = None


class TimerScreen(Screen, Themeable):
    """ TimerScreen Object contains all of the  control logic relating to the timer screen.
    The layout information of the Timer Screen is located in the 'timer.kv' file in the layouts
    directory.
    """
    # Theme Properties
    text_color = ListProperty(themes.THEME_CONTROLLER.text)

    # Functional Properties
    _clock_event = ObjectProperty()
    timer_active = BooleanProperty(False)  # True flags the timer as currently active
    timer_in_progress = BooleanProperty(False)  # True flags the timer as currently in one full state (paused/active)
    timer_type_selection = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.current_time = POMO_TIME
        self._timer_display_update()
        self.current_timer_function = None
        self.current_task_action = None
        self.task_action_type = 1

    def theme_update(self):
        self.text_color = self.theme.text
        self.text_color[3] = .8

    def switch_timer_type(self, selected):
        self.timer_type_selection = selected
        if not self.timer_active and not self.timer_in_progress:
            print("Changing Timer Types")
            if selected == 0:
                self.current_time = POMO_TIME
                self.task_action_type = 2
            elif selected == 1:
                self.current_time = SHORT_BREAK
                self.task_action_type = 4
            elif selected == 2:
                self.current_time = LONG_BREAK
                self.task_action_type = 5
            elif selected == 3:
                self.current_time = 0
                self.task_action_type = 6
        self._timer_display_update()

    def start_pause_trigger(self):
        task_id = self.ids.task_manager.selected.uuid
        if not self.timer_in_progress:
            if self.timer_type_selection == 3:
                self.current_timer_function = self._update
            else:
                self.current_timer_function = self._count_down

        if self.timer_active:
            self.ids.start_pause_button.text = 'Start'
            Clock.unschedule(self._clock_event)
            if self.timer_in_progress:
                self._complete_task_action()
                self.current_task_action = TaskAction(task_id, 3, datetime.now())
            self.timer_active = False
        else:
            self._clock_event = Clock.schedule_interval(self.current_timer_function, 0.016)
            self.ids.start_pause_button.text = 'Pause'
            if self.timer_in_progress:
                self._complete_task_action()
            self.timer_active = True
            self.timer_in_progress = True

        if not self.current_task_action:
            self.current_task_action = TaskAction(task_id, self.task_action_type, datetime.now())

    def timer_reset(self):
        if self.timer_active or self.timer_in_progress:
            self.timer_active = False
            self.timer_in_progress = False
            Clock.unschedule(self._clock_event)
            self._complete_task_action()
            self.ids.start_pause_button.text = 'Start'
            self.switch_timer_type(self.timer_type_selection)

    def _complete_task_action(self):
        self.current_task_action.finish_time = datetime.now()
        if not self.current_task_action.task_id == 0:  # TODO: Should no-task timer actions be recorded?
            DB.write_task_action(self.current_task_action)
        self.current_task_action = None

    def _timer_display_update(self):
        minutes, seconds = divmod(self.current_time, 60)
        self.ids.timer.text = ('[b]%02d[/b]:%02d' % (int(minutes), int(seconds)))

    def _update(self, nap):
        self.current_time += nap
        self._timer_display_update()

    def _count_down(self, nap):
        self.current_time -= nap
        minutes, seconds = divmod(self.current_time, 60)
        if self.current_time <= 0:
            self._count_down_alert()
            self.current_time = 0
        else:
            self.ids.timer.text = ('[b]%02d[/b]:%02d' % (int(minutes), int(seconds)))

    def _count_down_alert(self):
        # Use this function to trigger notifications and other logic when the
        # count down timer is finished.
        self.timer_reset()
        print("FINISHED")


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
        # TODO: What is the behavior when switching out a task mid timer session?
        self.selected = TaskDisplay(task.uuid, task.tasktext.text, task.notes, task.project.db_id)
        self.add_widget(self.selected)
        print(self.selected.uuid)
        print(self.selected.tasktext.text)

    def _reset_default_task(self):
        self.clear_widgets()
        self.add_widget(self.default)


class NoProjectSelectedButton(Button, Themeable):
    button_texture = StringProperty(themes.ALL_BEV_CORNERS)
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    text_color = ListProperty()
    button_color = ListProperty()
    shadow_color = ListProperty()

    def __init__(self, **kwargs):
        super(NoProjectSelectedButton, self).__init__(**kwargs)
        self.text = 'Select a project!'
        self.uuid = 0
        self.button_color = self.theme.tasks
        self.text_color = self.theme.text
        self.text_color[3] = .8
        self.shadow_color = themes.SHADOW_COLOR

    def theme_update(self):
        self.button_color = self.theme.tasks
        self.text_color = self.theme.text
        self.text_color[3] = .8


class TaskDisplay(Task):
    """ TaskDisplay inherits all the display functionality of the task widget
        without the control functionality.
    """
    def __init__(self, *args, **kwargs):
        super(TaskDisplay, self).__init__(*args, **kwargs)

    def on_press(self):
        # TODO: Switch screen back to task menu screen and wait to select task!
        pass

    def on_touch_down(self, touch):
        pass

    def on_touch_move(self, touch):
        pass

    def on_release(self):
        pass


class TimerButton(Button, Themeable):
    button_texture = StringProperty(themes.ALL_BEV_CORNERS)
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    text_color = ListProperty()
    button_color = ListProperty()
    shadow_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button_color = self.theme.tasks
        self.text_color = self.theme.text
        self.text_color[3] = .8
        self.shadow_color = themes.SHADOW_COLOR

    def theme_update(self):
        self.button_color = self.theme.tasks
        self.text_color = self.theme.text
        self.text_color[3] = .8
        self.on_state(self, 0)

    def on_state(self, widget, value):
        if self.state == 'down':
            self.button_color = self.theme.selected
        else:
            self.button_color = self.theme.tasks


class TimerSettingsButton(ToggleButton, Themeable):
    button_texture = StringProperty(themes.ALL_BEV_CORNERS)
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    text_color = ListProperty()
    button_color = ListProperty()
    shadow_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Theme Init Stuff
        self.button_color = self.theme.tasks
        text = self.theme.text
        text[3] = .8
        self.text_color = text
        self.shadow_color = themes.SHADOW_COLOR

    def theme_update(self):
        self.button_color = self.theme.tasks
        text = self.theme.text
        text[3] = .8
        self.text_color = text
        self.on_state(self, 0)

    def on_state(self, widget, value):
        if self.state == 'down':
            self.button_color = self.theme.selected
        else:
            self.button_color = self.theme.tasks

    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)
