from kivy.uix.screenmanager import Screen


from tasktracker.database.db_interface import DB
from tasktracker.stats.timeline import TaskTimeLine, VisualTimeTick, PeriodDisplayTick, RecordPeriod
from datetime import datetime, timezone, timedelta

# TODO: Load task action history data based on specific date range.
# Todo: Develop custom time line class that is like data list tick but for time periods.


class StatsScreen(Screen):  # TODO: Break this out into it's own module eventually.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.test_time_start = datetime(year=2017, month=2, day=7, hour=1, minute=50, tzinfo=timezone.utc)
        self.test_time_end = datetime(year=2017, month=2, day=7, hour=4, minute=18, second=6, tzinfo=timezone.utc)
        self.time_buffer = timedelta(minutes=1)

        DB.load_task_actions(self.test_time_start, self.test_time_end, self._test_load_projects)

        # self.time_ticks = []
        self.time_ticks = [VisualTimeTick(mode=VisualTimeTick.mode.options[i], valign='line_bottom') for i in
                           [0, 2, 5, 6, 7, 9, 10]]

        self.time_ticks.extend([VisualTimeTick(mode=VisualTimeTick.mode.options[i], valign='line_top') for i in
                               [0, 2, 5, 6, 7, 9, 10]])

        print(self.time_ticks)

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
            for t_key, t_value in value.items():
                if t_key == 2:
                    self.time_ticks.append(PeriodDisplayTick(data=t_value, valign='line_top'))

                else:
                    self.time_ticks.append(PeriodDisplayTick(data=t_value, valign='line_bottom'))

        self.test_timeline = TaskTimeLine(orientation='horizontal', ticks=self.time_ticks, line_width=1)

        self.test_timeline.center_on_timeframe(self.test_time_start - self.time_buffer,
                                               self.test_time_end + self.time_buffer)
        self.test_timeline.cover_background = False
        self.add_widget(self.test_timeline)







