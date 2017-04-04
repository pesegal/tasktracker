from kivy.uix.bubble import Bubble
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import sp
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock

from tasktracker.themes.themes import THEME_CONTROLLER, Themeable
from tasktracker.themes import themes


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

    def update_date(self, dt):
        self.text = dt.strftime('%m/%d/%Y')

    def insert_text(self, substring, from_undo=False):
        if self.cursor[0] == 1 or self.cursor[0] == 4:
            substring += '/'
        if not from_undo and (len(self.text) + len(substring) > self.max_chars):
            return
        super(VDateInput, self).insert_text(substring, from_undo)

    def on_text_validate(self):
        try:
            #TODO: Make the labels set the date.
        except ValueError:
            pass


class VTimeInput(ValidatedTextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_chars = 5

    def update_time(self, dt):
        self.text = dt.strftime('%I:%M')
        # TODO: Switch between AM/PM selctions

    def insert_text(self, substring, from_undo=False):
        if self.cursor[0] == 1:
            substring += ':'
        if not from_undo and (len(self.text) + len(substring) > self.max_chars):
            return
        super(VTimeInput, self).insert_text(substring, from_undo)


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