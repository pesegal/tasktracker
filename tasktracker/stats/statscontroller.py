from kivy.uix.screenmanager import Screen
from kivy.garden.timeline import Timeline, TimeTick, selected_time_ticks, round_time
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from kivy.metrics import dp

from tasktracker.database.db_interface import DB

from datetime import datetime, timezone, timedelta
from tasktracker.settings import to_datetime, to_local_time

from tasktracker.settings import APP_CONTROL
from tasktracker.themes import themes


class RecordPeriod:
    """ A data structure that contains the period data.
    """
    def __init__(self, record_id, action_type, start_time, end_time, task_id, project_id=None):
        self.record_id = record_id
        self.action_type = action_type
        self.start_time = start_time
        self.end_time = end_time
        self.task_id = task_id
        self.project_id = project_id

    def __str__(self):
        print("""RecordPeriod ID# %s
                  Task_ID:     %s
                  Project_ID:  %s
                  Start_Time:  %s
                  End_Time:    %s
                  Action_Type: %s
              """)

# TODO: Load task action history data based on specific date range.
# Todo: Develop custom time line class that is like data list tick but for time periods.


class PeriodDisplayTick(TimeTick):
    data_list = ListProperty([])
    tick_height = NumericProperty(30)

    def __init__(self, data, tick_height=30, *args, **kw):
        super(PeriodDisplayTick, self).__init__(*args, **kw)
        self.data_list = data
        self.tick_height = tick_height

    def tick_iter(self, tl):
        """ Override :meth: 'TimeTick.tick_iter'
            Returns RecordPeriod object's that fall within the current min and max display times.
        """
        if self.scale(tl.scale) < self.min_space:
            raise StopIteration

        time_min, time_max = self.time_min_max(tl, extended=True)

        try:
            data_index = self._starting_index(time_min, time_max)
            if data_index is None:
                raise StopIteration

            while self.data_list[data_index].start_time < time_max:
                yield self.data_list[data_index]
                data_index += 1

        except IndexError:
            raise StopIteration

    def _starting_index(self, time_min, time_max):
        """ This function will return the index of the first record that falls within the display screen. If no
        records match this then it will return None.
        """
        for record in self.data_list:
            if record.start_time > time_min:
                if not record.start_time > time_max:
                    return self.data_list.index(record)
                else:
                    return None
        return None

    def draw(self, tickline, record, return_only=False):
        tick_pos, record_index = self.pos_index_of(tickline, record.start_time)
        end_pos = self.pos_of(tickline, record.end_time)

        tw, th = (end_pos - tick_pos, self.tick_height)
        if tickline.is_vertical():
            halign = self.halign
            if halign == 'left':
                x = tickline.x
            elif halign == 'line_left':
                x = tickline.line_pos - th
            elif halign == 'line_right':
                x = tickline.line_pos
            else:
                x = tickline.right - th
            y = tick_pos - tw / 2
            height, width = tw, th
            if not return_only:
                self._vertices.extend([x, y, 0, 0,
                                       x, y + height, 0, 0,
                                       x + width, y + height, 0, 0,
                                       x + width, y, 0, 0,
                                       x, y, 0, 0,
                                       x, y + height, 0, 0])
        else:
            valign = self.valign
            if valign == 'top':
                y = tickline.top - th
            elif valign == 'line_top':
                y = tickline.line_pos
            elif valign == 'line_bottom':
                y = tickline.line_pos - th
            else:
                y = tickline.y
            x = tick_pos - tw / 2
            width, height = tw, th
            if not return_only:
                self._vertices.extend([x, y, 0, 0,
                                       x + width, y, 0, 0,
                                       x + width, y + height, 0, 0,
                                       x, y + height, 0, 0,
                                       x, y, 0, 0,
                                       x + width, y, 0, 0])

        tick_rect = (x, y, width, height)
        tickline.labeller.regester(self, record_index, tick_rect)

    def get_label_texture(self, index, succeinct=True, return_kw=False, return_lable=False, **kw):
        # TODO: Look into what might be the best way to display this information. Project or task or total time?
        # Todo: Figure out how to do labeling correctly
        return None

    def on_touch_down(self, touch):
        pass

    # TODO: Develop a function that will return the current displayed period on a click.


# TODO: Develop test data to do the display correctly.

# Todo: Figure out what the default date range is. For Testing make it all time?
# TODO: Look into figuring out how to return more data when clicking on a specific item.Create a bubble popup with data.


class TaskTimeLine(Timeline):
    testview = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        now = datetime.now(timezone.utc)
        past_hour = now - timedelta(hours=1)

        self.max_time = now

        # Todo: Look into having to date selectors attached the screen to view work periods.
        #self.center_on_timeframe(past_hour, now)

    def redraw_(self, *args):
        super().redraw_(*args)
        # print(self.time_0, self.time_1, 'Scale:', self.scale)

    def _print_stuff(self, *args):
        print(*args)

    # Todo: Tie scale to a slider.


class StatsScreen(Screen):  # TODO: Break this out into it's own module eventually.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        test_time_start = datetime(year=2017, month=2, day=7, hour=1, minute=50, tzinfo=timezone.utc)
        test_time_end = datetime(year=2017, month=2, day=7, hour=2, minute=2, second=6, tzinfo=timezone.utc)

        print(test_time_start, test_time_end)

        DB.load_task_actions(test_time_start, test_time_end, self._test_load_projects)

        # time_ticks = [TimeTick(mode=TimeTick.mode.options[i], valign='line_top') for i in [0, 3, 5, 7, 9, 10, 12, 14, 15]]
        # time_ticks.append(TaskTimeTicks(valign='line_top'))
        #
        #test_timeline = TaskTimeLine(orientation='horizontal', ticks=time_ticks, line_width=1.)
        #test_timeline.time_0 =
        # test_timeline.cover_background = False
        # self.add_widget(test_timeline)

    def _test_load_projects(self, data, tb):
        # Function callback to test the database interface for loading projects.
        for item in data:
            #TODO: Need to get the project ID from the task ID.
            print(RecordPeriod(item[4], to_local_time(to_datetime(item[2])), to_local_time(to_datetime(item[3])),
                               item[1]))



