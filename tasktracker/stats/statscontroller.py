from kivy.uix.screenmanager import Screen
from kivy.garden.timeline import Timeline, TimeTick, selected_time_ticks, round_time
from kivy.properties import ObjectProperty, ListProperty
from kivy.metrics import dp

from datetime import datetime, timezone, timedelta

from tasktracker.settings import APP_CONTROL
from tasktracker.themes import themes


class RecordPeriod:
    """ A data structure that contains the period data.
    """
    def __init__(self, action_type, start_time, end_time, project_id=None):
        self.action_type = action_type
        self.start_time = start_time
        self.end_time = end_time
        self.project_id = project_id

# TODO: Load task action history data based on specific date range.
# Todo: Develop custom time line class that is like data list tick but for time periods.


class PeriodDisplayTick(TimeTick):
    data_list = ListProperty([])

    def __init__(self, data, *args, **kw):
        super(PeriodDisplayTick, self).__init__(*args, **kw)
        self.data_list = data

    def tick_iter(self, tl):
        if self.scale(tl.scale) < self.min_space:
            raise StopIteration

        time_min, time_max = self.time_min_max(tl, extended=True)

        try:
            # return the index of the first record that has a beginning or end time that is greater then min_time


            # while condition()
                # continue to return RecordPeriod Objects until either there are no more objects
                # or the start time of the object is > then the time_max!


        except IndexError:
            raise StopIteration





        # time = round_time(time_min, self.mode, 'up')
        #
        # delta = timedelta(seconds=self.granularity(self.mode))
        #
        # if self.mode == 'day' and tl.backward:
        #     yield time - timedelta(days=1)
        # while time <= time_max:
        #     yield time
        #     time += delta
        # if self.mode == 'day' and not tl.backward:
        #     yield time
        # raise StopIteration



    def draw(self, tickline, time):
        # This needs to be over written so that it draws the data instead. To draw_tick
        pass


    # Todo: Figure out how to do labeling correctly

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

        # time_ticks = [TimeTick(mode=TimeTick.mode.options[i], valign='line_top') for i in [0, 3, 5, 7, 9, 10, 12, 14, 15]]
        # time_ticks.append(TaskTimeTicks(valign='line_top'))
        #
        # test_timeline = TaskTimeLine(orientation='horizontal', ticks=time_ticks, line_width=1.)
        # test_timeline.cover_background = False
        # self.add_widget(test_timeline)

        PeriodDisplayTick(data=[1,2,3,4,5])

