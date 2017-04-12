from kivy.uix.bubble import Bubble
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import sp
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock

from tasktracker.themes.themes import THEME_CONTROLLER, Themeable
from tasktracker.settings import to_local_time
from tasktracker.themes import themes

from datetime import date, datetime, time


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
        self.error_text = "Incorrect Date Format"

    def update_date(self, dt):
        self.text = dt.strftime('%m/%d/%Y')

    def insert_text(self, substring, from_undo=False):
        print(substring, self.cursor, len(self.text))
        if (self.cursor[0] == 1 or self.cursor[0] == 4) and len(self.text) <= self.cursor[0]:
            substring += '/'
        if not from_undo and (len(self.text) + len(substring) > self.max_chars):
            return
        super(VDateInput, self).insert_text(substring, from_undo)

    def on_focus(self, this, focused):
        if self.text == self.error_text and focused:  # Auto reset the text box on date input failure
            self.text = ''

    def on_text_validate(self):
        try:
            month, day, year = self.text.split('/')
            month = int(month)
            day = int(day)
            year = int(year)
            d = date(month=month, day=day, year=year)
            self.selection_menu.update_timeline(update_date=d)
        except ValueError as err:
            print(err)
            self.text = self.error_text
        except VInputError as err:
            print(err.message)
            self.text = err.message


class VTimeInput(ValidatedTextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_chars = 5
        self.error_message = "Incorrect Time"

    def update_time(self, dt):
        self.text = dt.strftime('%I:%M')
        # TODO: Switch between AM/PM selctions

    def insert_text(self, substring, from_undo=False):
        if self.cursor[0] == 1:
            substring += ':'
        if not from_undo and (len(self.text) + len(substring) > self.max_chars):
            return
        super(VTimeInput, self).insert_text(substring, from_undo)

    def on_text_validate(self):
        try:
            hour, minute = self.text.split(':')
            hour = int(hour)
            minute = int(minute)
            t = time(hour=hour, minute=minute)
            # TODO: Get AM PM
            self.selection_menu.update_timeline(update_time=t)
        except ValueError as err:
            print(err)
            self.text = self.error_message
        except VInputError as err:
            self.text = err.message


class DateTimeLabel(Label, Themeable):
    display_time = ObjectProperty()
    time_line_container = ObjectProperty()
    name = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(display_time=self.update_label)

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

    # TODO: Label display is directly tied current max mins display time of the timeline.

    # TODO: Auto format (add slashes) text input to match datetime.

    # TODO: Allow both datetime selection boxes to be open at once.


class StatsTimeSelectionMenu(Bubble, Themeable):
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    bg_texture = StringProperty(themes.ALL_BEV_CORNERS)
    bg_color = ListProperty([0, 0, 0, .5])

    time_line = ObjectProperty()

    def __init__(self, dt, label, timeline, **kwargs):
        super().__init__(**kwargs)
        self.datetime = dt
        self.label = label
        self.size = (300, 100)
        self.time_line = timeline
        self.update_date = self.datetime.date()
        self.update_time = self.datetime.time()

        print(self.label.name)
        if self.label.name == "label_time_start":
            self.pos = self.label.x + sp(5), self.label.height + 5
            self.arrow_pos = "bottom_left"
        else:
            self.pos = self.label.x + self.label.width - self.width - sp(5), self.label.height + 5
            self.arrow_pos = "bottom_right"

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
        if update_time:
            self.update_time = update_time

        print(self.update_date, self.update_time)

        update_datetime = to_local_time(datetime.combine(self.update_date, self.update_time))

        if self.label.name == 'label_time_start':
            if update_datetime > self.time_line.time_1:
                raise VInputError('Start date > end date.')
            self.time_line.index_0 = self.time_line.index_of(update_datetime)
        else:
            if update_datetime < self.time_line.time_0:
                raise VInputError('End date < start date.')
            self.time_line.index_1 = self.time_line.index_of(update_datetime)

    def update_input_datetime(self, dt=None):
        if dt:
            self.ids.date_input.update_date(dt)
            self.ids.time_input.update_time(dt)
        else:
            self.ids.date_input.update_date(self.datetime)
            self.ids.time_input.update_time(self.datetime)

    def _close_menu(self):
        self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            self._close_menu()
        elif 'button' in touch.profile and touch.button != 'left':
            self._close_menu()
        else:
            return super().on_touch_down(touch)