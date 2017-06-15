from kivy.uix.bubble import Bubble
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.metrics import sp
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock
from kivy.animation import Animation


from tasktracker.themes.themes import THEME_CONTROLLER, Themeable
from tasktracker.settings import to_local_time, timezone_local
from tasktracker.themes import themes

from datetime import date, datetime, time, timedelta


class VInputError(Exception):
    def __init__(self, message):
        self.message = message


class ValidatedTextInput(TextInput, Themeable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False

    def theme_update(self):
        pass


class VDateInput(ValidatedTextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_chars = 10
        self.current_date = None

    def update_date(self, dt):
        self.text = dt.strftime('%m/%d/%Y')
        self.current_date = dt.date()

    def insert_text(self, substring, from_undo=False):
        print(substring, self.cursor, len(self.text))
        if (self.cursor[0] == 1 or self.cursor[0] == 4) and len(self.text) <= self.cursor[0]:
            substring += '/'
        if not from_undo and (len(self.text) + len(substring) > self.max_chars):
            return
        super(VDateInput, self).insert_text(substring, from_undo)

    def on_text_validate(self):
        try:
            month, day, year = self.text.split('/')
            month = int(month)
            day = int(day)
            year = int(year)
            self.current_date = date(month=month, day=day, year=year)
            self.selection_menu.update_timeline(update_date=self.current_date)
        except ValueError as err:
            self.selection_menu.parent.open_error_notification_popup(str(err).capitalize())


class VTimeInput(ValidatedTextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_chars = 5
        self.current_time = None

    def update_time(self, dt):
        self.text = dt.strftime('%I:%M')
        self.current_time = dt.timetz()
        # TODO: Switch between AM/PM selections

    def insert_text(self, substring, from_undo=False):
        if self.cursor[0] == 1 and len(self.text) <= self.cursor[0]:
            substring += ':'
        if not from_undo and (len(self.text) + len(substring) > self.max_chars):
            return
        super(VTimeInput, self).insert_text(substring, from_undo)

    def on_text_validate(self):
        try:
            hour, minute = self.text.split(':')
            hour = int(hour)
            minute = int(minute)
            # Handling AM/PM
            self.current_time = time(hour=hour, minute=minute, tzinfo=timezone_local)
            self.selection_menu.update_timeline(update_time=self.current_time)
        except ValueError as err:
            self.selection_menu.parent.open_error_notification_popup(str(err).capitalize())


class UpdateButton(Button, Themeable):
    date_input = ObjectProperty()
    time_input = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        pass

    def update(self):
        self.date_input.on_text_validate()
        self.time_input.on_text_validate()


class DateTimeLabel(Label, Themeable):
    display_time = ObjectProperty()
    time_line_container = ObjectProperty()
    name = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(display_time=self.update_label)
        self.bubble_selection_menu = None

    def theme_update(self):
        pass

    def on_touch_down(self, touch):
        # filter touch events
        if self.collide_point(touch.x, touch.y) and 'button' in touch.profile and touch.button == 'right':
            print(self, "was touched!")
            self.time_line_container.open_dt_selection_menu(self.display_time, self)

    def update_label(self, date, dt):
        local_datetime = dt
        self.text = "[b]{}[/b]\n{}".format(local_datetime.strftime("%d %B"), local_datetime.strftime("%I:%M %p"))

    # TODO: Label display is directly tied current max/mins display time of the timeline.

    # TODO: Auto format (add slashes) text input to match datetime.

    # TODO: Allow both datetime selection boxes to be open at once.


class StatsTimeSelectionMenu(Bubble, Themeable):
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    bg_texture = StringProperty(themes.ALL_BEV_CORNERS)
    bg_color = ListProperty([0, 0, 0, .5])

    time_line = ObjectProperty()
    dt_toggle_am = ObjectProperty()
    dt_toggle_pm = ObjectProperty()

    def __init__(self, dt, label, timeline, **kwargs):
        super().__init__(**kwargs)
        self.datetime = dt
        self.label = label
        self.size = (300, 100)
        self.time_line = timeline
        self.update_date = self.datetime.date()
        self.update_time = self.datetime.time()

        self.label.bubble_selection_menu = self

        if self.label.name == "label_time_start":
            self.pos = self.label.x + sp(5), self.label.height + sp(5)
            self.arrow_pos = "bottom_left"
            self.dt_toggle_am.group = "am_pm_start"
            self.dt_toggle_pm.group = "am_pm_start"
        else:
            self.pos = self.label.x + self.label.width - self.width - sp(5), self.label.height + sp(5)
            self.arrow_pos = "bottom_right"
            self.dt_toggle_am.group = "am_pm_end"
            self.dt_toggle_pm.group = "am_pm_end"

        # Set the am-pm buttons.
        print(self.datetime.hour)
        if 0 <= self.datetime.hour < 12:
            self.set_am_pm(True)
        else:
            self.set_am_pm(False)

        self.update_input_datetime()

    def theme_update(self):
        self.bg_color = self.theme.status

    def update_timeline(self, update_date=None, update_time=None):
        """ Takes either a date or a time object and combines them together into a datetime object and
        updates the timeline displayed time.

        :param update_date: Date object or None
        :param update_time: Time object or None
        """
        if update_date:
            self.update_date = update_date
            self.update_time = self.ids.time_input.current_time
        if update_time:
            self.update_time = update_time
            self.update_date = self.ids.date_input.current_date
            if self.update_time.hour < 12 and not self.get_am_pm():  # Check to see if PM is selected.
                self.update_time = time(self.update_time.hour + 12, self.update_time.minute,
                                        tzinfo=self.update_time.tzinfo)
            elif self.update_time.hour == 12 and self.get_am_pm():  # check to see if it is 12 AM
                self.update_time = time(self.update_time.hour - 12, self.update_time.minute,
                                        tzinfo=self.update_time.tzinfo)
            elif 24 >= self.update_time.hour > 12:  # Set selection button to PM if military time
                self.set_am_pm(False)
                visual_time = time(self.update_time.hour - 12, self.update_time.minute,
                                   tzinfo=self.update_time.tzinfo)
                self.ids.time_input.text = visual_time.strftime('%I:%M')

        update_datetime = datetime.combine(self.update_date, self.update_time)
        print(update_datetime)

        # TODO: Check to make sure that the date time selection works correctly.

        try:
            if self.label.name == 'label_time_start':
                if update_datetime > self.time_line.time_1:
                    raise VInputError('Date range overlap')
                self.time_line.index_0 = self.time_line.index_of(update_datetime)
            else:
                if update_datetime < self.time_line.time_0:
                    raise VInputError('Date range overlap')
                self.time_line.index_1 = self.time_line.index_of(update_datetime)
            self.label.update_label(self, update_datetime)
        except VInputError as err:
            self.parent.open_error_notification_popup(err.message)

        print("Timeline Scale: ", self.time_line.scale)

    def update_input_datetime(self, dt=None):
        if dt:
            self.ids.date_input.update_date(dt)
            self.ids.time_input.update_time(dt)
        else:
            self.ids.date_input.update_date(self.datetime)
            self.ids.time_input.update_time(self.datetime)

    def set_am_pm(self, am):
        """
        :param am: set to true if you want to set the button state to AM else false for PM
        """
        if am:
            self.ids.am_button.state = 'down'
            self.ids.pm_button.state = 'normal'
        else:
            self.ids.pm_button.state = 'down'
            self.ids.am_button.state = 'normal'

    def get_am_pm(self):
        """
        :return: True if AM / False if PM
        """
        if self.dt_toggle_am.state == 'down':
            return True
        else:
            return False

    def _close_menu(self):
        self.label.bubble_selection_menu = None
        self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        if not (not self.label.time_line_container.touch_label_check(touch) or not (
                'button' in touch.profile)) and touch.button == 'right':
            return super().on_touch_down(touch)
        elif not self.label.time_line_container.touch_label_check(touch):
            self._close_menu()
        elif 'button' in touch.profile and touch.button != 'left':
            self._close_menu()
        else:
            return super().on_touch_down(touch)

        # TODO: Get update button to work

        # TODO: Create scrolling zoom bar

        # TODO: Create timeline display logic.

class ThemedBubblePopup(Bubble, Themeable):
    """ This is a parent class that all the notification bubble popups on the stats screen
    are derived from to share themeing logic.

    """
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    bg_texture = StringProperty(themes.ALL_BEV_CORNERS)
    bg_color = ListProperty([0, 0, 0, .5])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        self.bg_color = self.theme.status


class ErrorNotificationPopup(ThemedBubblePopup):
    message = StringProperty('None')

    def __init__(self, message, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        Clock.schedule_once(self.remove_self, 2)

    def remove_self(self, *args):
        err_animation = Animation(size=(self.width, 10),
                                  duration=.2, t='in_cubic')
        err_animation.bind(on_complete=lambda *a: self.parent.remove_widget(self))
        err_animation.start(self)


# ToDo Create popup that displays the correct zoom level date range
class SliderNotificationPopup(ThemedBubblePopup):
    message = StringProperty('None')

    def __init__(self, message, **kwargs):
        super().__init__(**kwargs)
        self.message = message

    def set_message(self, message):
        self.message = message


class TimelineSlider(Slider, Themeable):
    time_line_container = ObjectProperty()

    # Returns the number of minutes for that period.
    zoom_dict = {
        # ... index starts at 10 to allow for smaller values in the future
        10: ['30 minutes', 30],
        11: ['1 hour', 60],
        12: ['2 hours', 120],
        13: ['4 hours', 240],
        14: ['8 hours', 480],
        15: ['12 hours', 720],
        16: ['1 day', 1440],
        17: ['2 days', 2880],
        18: ['5 days', 7200],
        19: ['10 days', 14400],
        20: ['14 days', 20160],
        21: ['1 month', 43800],
        22: ['2 months', 87600],
        23: ['3 months', 131400],
        24: ['6 months', 262800],
        25: ['1 year', 525600]
        # 26, ['all time', 38400]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.zoom_dict = TimelineSlider.zoom_dict
        self.zoom_levels = []
        self.current_desc = "None"
        self.min = 10
        self.max = 25
        self.value = 18
        self.step = 1
        self.moved_flag = False
        self.bind(value=self._adjust_slider)

    def theme_update(self):
        pass

    def _get_zoom_level_and_title(self, value):
        return self.zoom_dict[value][0], self.zoom_dict[value][1]

    def _adjust_slider(self, object, value):
        if self.time_line_container:
            timeline = self.time_line_container.timeline
            self.current_desc, delta_min = self._get_zoom_level_and_title(value)
            zoom_date = timeline.time_1 - timedelta(minutes=delta_min)
            self.moved_flag = True
            timeline.index_0 = timeline.index_of(zoom_date)

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        if self.moved_flag:
            self.time_line_container.update_slider_notification_popup(touch, self.current_desc)
            self.moved_flag = False


