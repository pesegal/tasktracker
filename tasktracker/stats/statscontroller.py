from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label


from tasktracker.database.db_interface import DB
from tasktracker.stats.timeline import TaskTimeLine, VisualTimeTick, PeriodDisplayTick, RecordPeriod
from datetime import datetime, timezone, timedelta
from tasktracker.task.taskpopups import PROJECT_LIST
from tasktracker.themes.themes import THEME_CONTROLLER
from kivy.utils import get_color_from_hex

# TODO: DEFAULT COLORS FOR SHORT BREAK, LONG BREAK, & PAUSE (MAKE THESE CONFIGURABLE IN SETTINGS?)


class DateTimeLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # TODO: Build out clickable date time input.
    # TODO: Label display is directly tied current max mins display time of the timeline.


class TimelineContainer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _test_load_projects(self, data, tb):
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

        self.test_timeline = TaskTimeLine(orientation='horizontal', ticks=self.time_ticks, line_width=1)

        self.test_timeline.center_on_timeframe(self.test_time_start - self.time_buffer,
                                               self.test_time_end + self.time_buffer)
        self.test_timeline.cover_background = False
        self.add_widget(self.test_timeline)


class StatsScreen(Screen):  # TODO: Break this out into it's own module eventually.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.test_time_start = datetime(year=2017, month=2, day=7, hour=1, minute=50, tzinfo=timezone.utc)
        self.test_time_end = datetime(year=2017, month=2, day=20, hour=4, minute=18, second=6, tzinfo=timezone.utc)
        self.time_buffer = timedelta(minutes=1)



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



