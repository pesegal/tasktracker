from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.slider import Slider
from kivy.uix.bubble import Bubble
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty
from kivy.utils import get_color_from_hex


from tasktracker.database.db_interface import DB
from tasktracker.stats.timeline import TaskTimeLine, VisualTimeTick, PeriodDisplayTick, RecordPeriod
from datetime import datetime, timezone, timedelta
from tasktracker.task.taskpopups import PROJECT_LIST
from tasktracker.themes.themes import THEME_CONTROLLER, Themeable
from tasktracker.settings import to_local_time


# TODO: DEFAULT COLORS FOR SHORT BREAK, LONG BREAK, & PAUSE (MAKE THESE CONFIGURABLE IN SETTINGS?)

# Todo: write a helper function that takes start and end datetimes and returns the number of months, weeks, days

class DateTimeLabel(Label, Themeable):
    display_time = ObjectProperty()
    time_line_container = ObjectProperty()
    name = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(display_time=self.update_label)

    def theme_update(self):
        pass

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y) :  # filter touch events
            print(self, "was touched!")
            self.time_line_container.open_dt_selection_menu(self.display_time, self)

    def update_label(self, date, dt):
        local_datetime = dt
        self.text = "[b]{}[/b]\n{}".format(local_datetime.strftime("%d %B"), local_datetime.strftime("%I:%M %p"))

    # TODO: Label display is directly tied current max mins display time of the timeline.


# TODO: Work on themeing the bubble and getting proper datetime input built.
class StatsTimeSelectionMenu(Bubble):
    def __init__(self, dt, label, **kwargs):
        super().__init__(**kwargs)
        self.datetime = dt
        self.label = label
        self.size = (300, 100)

        print(self.label.name)
        if self.label.name == "label_time_start":
            self.pos = self.label.x, self.label.height + 5
            self.arrow_pos = "bottom_left"
        else:
            self.pos = self.label.x + self.label.width - self.width, self.label.height + 5
            self.arrow_pos = "bottom_right"

    def _close_menu(self):
        self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            self._close_menu()
        elif 'button' in touch.profile and touch.button != 'left':
            self._close_menu()
        else:
            return super().on_touch_down(touch)


class TimelineSlider(Slider):
    time_line_container = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.min = 10
        self.max = 500000
        self.value = 1000
        self.bind(value=self._print_value)

    def _print_value(self, *args):
        print(args)
        if self.time_line_container:
            # TODO: Convert this into a stepped time.
            self.time_line_container.timeline.scale = args[1]


class TimelineContainer(FloatLayout):
    """ TimelineContainer object contains all functionality related to the display and manipulation
        of the timeline.
    """

    display_time_start = ObjectProperty(None)
    display_time_end = ObjectProperty(None)
    timeline = ObjectProperty()

    label_start = ObjectProperty()
    label_end = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.bind(display_time_start=self._display_time_update)
        # self.bind(display_time_end=self._display_time_update)
        self.time_ticks = [VisualTimeTick(mode=VisualTimeTick.mode.options[i], valign='line_bottom') for i in
                           [0, 2, 5, 6, 7, 9, 10]]
        self.time_ticks.extend([VisualTimeTick(mode=VisualTimeTick.mode.options[i], valign='line_top',
                                               tick_color=[1,1,1,1]) for i in [0, 2, 5, 6, 7, 9, 10]])

        today = datetime.now(tz=timezone.utc)
        t_buffer = timedelta(days=60)

        self.display_time_start = datetime(year=today.year, month=today.month, day=today.day,
                                           hour=0, minute=0, tzinfo=timezone.utc)
        self.display_time_end = datetime(year=today.year, month=today.month, day=today.day,
                                         hour=23, minute=0, tzinfo=timezone.utc)

        DB.load_task_actions(self.display_time_start - t_buffer,
                             self.display_time_end + t_buffer, self._display_timeline)
        print(self.ids)

    def open_dt_selection_menu(self, dt, label):
        self.add_widget(StatsTimeSelectionMenu(dt, label))



    def _display_timeline(self, data, tb):
        # Function callback to test the database interface for loading projects.

        # TODO: Split Records by Project Type and Action Type
        project_dict = dict()

        for item in data:
            record = RecordPeriod(*item)
            print(record)

            if record.project_id in project_dict.keys():
                if record.action_type in project_dict[record.project_id].keys():
                    project_dict[record.project_id][record.action_type].append(record)
                else:
                    project_dict[record.project_id][record.action_type] = [record]
            else:
                project_dict[record.project_id] = {record.action_type: [record]}

        for key, value in project_dict.items():
            print(key, value)

            # Get Project Color Else Default
            project = PROJECT_LIST.return_project_by_id(key)
            if project.color is None:
                p_color = THEME_CONTROLLER.selected
            else:
                p_color = get_color_from_hex(project.color)

            p_color[3] = .7 # Add some transparency to the timeline.

            for t_key, t_value in value.items():
                if t_key == 2:
                    self.time_ticks.append(PeriodDisplayTick(data=t_value, valign='line_top',
                                                             tick_color=p_color))
                else:
                    self.time_ticks.append(PeriodDisplayTick(data=t_value, valign='line_bottom',
                                                             tick_color=THEME_CONTROLLER.selected,
                                                             tick_height=20, line_offset=1))

        self.timeline = TaskTimeLine(self, orientation='horizontal', ticks=self.time_ticks, line_width=1)

        self.timeline.center_on_timeframe(self.display_time_start,
                                          self.display_time_end)
        self.timeline.cover_background = False
        self.add_widget(self.timeline, index=1)





class StatsScreen(Screen):  # TODO: Break this out into it's own module eventually.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)




        # DB.load_task_actions(self.test_time_start, self.test_time_end, self._test_load_projects)
        #
        # # self.time_ticks = []
        # self.time_ticks = [VisualTimeTick(mode=VisualTimeTick.mode.options[i], valign='line_bottom') for i in
        #                    [0, 2, 5, 6, 7, 9, 10]]
        #
        # self.time_ticks.extend([VisualTimeTick(mode=VisualTimeTick.mode.options[i], valign='line_top',
        #                                        tick_color=[1,1,1,1]) for i in [0, 2, 5, 6, 7, 9, 10]])
        #
        # print(self.time_ticks)



