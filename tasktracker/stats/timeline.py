""" Timeline module contains all the customized timeline display code. And the record period object that is used
to store that data once loaded from the database.

"""

from numbers import Number
from datetime import timedelta
from tasktracker.settings import to_datetime, to_local_time

from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from kivy.garden.timeline import Timeline, TimeTick, selected_time_ticks, round_time
from kivy.metrics import dp

from tasktracker.themes.themes import Themeable

from tasktracker.settings import APP_CONTROL


# from kivy.graphics import InstructionGroup, Mesh
# from kivy.graphics.context_instructions import Color


class RecordPeriod:
    """ A data structure that contains the period data.
    """
    def __init__(self, record_id, task_id, start_time, end_time, action_type, project_id=None):
        self.record_id = record_id
        self.action_type = action_type
        self.start_time = to_local_time(to_datetime(start_time))
        self.end_time = to_local_time(to_datetime(end_time))
        self.task_id = task_id
        self.project_id = project_id

    def __str__(self):
        time_display = '%Y-%m-%d %H:%M:%S.%f %Z'
        return """RecordPeriod ID# %s ----------------------------------------------
                  Task_ID:     %s
                  Project_ID:  %s
                  Start_Time:  %s
                  End_Time:    %s
                  Action_Type: %s
              """ % (self.record_id, self.task_id, self.project_id,
                     self.start_time.strftime(time_display), self.end_time.strftime(time_display),
                     self.action_type)


class VisualTimeTick(TimeTick, Themeable):

    size_dict = \
        {'day': [dp(1), dp(48)],
         '12 hours': [dp(1), dp(25)],
         '6 hours': [dp(1), dp(25)],
         '4 hours': [dp(1), dp(20)],
         '2 hours': [dp(1), dp(20)],
         'hour': [dp(1), dp(20)],
         '30 minutes': [dp(1), dp(12)],
         '15 minutes': [dp(1), dp(12)],
         '10 minutes': [dp(1), dp(8)],
         '5 minutes': [dp(1), dp(8)],
         'minute': [dp(1), dp(8)],
         '30 seconds': [dp(1), dp(7)],
         '15 seconds': [dp(1), dp(7)],
         '10 seconds': [dp(1), dp(4)],
         '5 seconds': [dp(1), dp(4)],
         'second': [dp(1), dp(4)]}

    def theme_update(self):
        self.tick_color = self.theme.text

    # TODO: Figure how how to correctly theme the labels.
    def get_label_texture(self, index, succinct=True, return_kw=False,
                          return_label=False, **kw):
        if isinstance(index, Number):
            t = self.datetime_of(index)
        else:
            t = index
        if self.mode == 'second':
            return None
        if self.mode == 'day':
            # need to get the datetime of the previous day
            text = (t - timedelta(seconds=1)).strftime('%a\n%m-%d-%y')
            kw.setdefault('height', 50)
        elif 'second' not in self.mode and succinct:
            text = str(t.time())[:-3]
        else:
            text = str(t.time())
        kw.setdefault('height', 20)
        kw['text'] = text
        kw['color'] = self.tick_color
        if return_kw:
            return kw
        if not return_label:
            return CoreLabel(**kw).texture
        label = AutoSizeLabel(**kw)
        label.texture_update()
        return label

        # TODO Figure out how to redraw the labels when the theme is changed.


class PeriodDisplayTick(TimeTick):
    data_list = ListProperty([])
    tick_height = NumericProperty(30)
    line_offset = NumericProperty(0)

    def __init__(self, data, tick_height=35, *args, **kw):
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
            if record.start_time > time_min or record.end_time > time_min:
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
                x = tickline.line_pos - (th + self.line_offset)
            elif halign == 'line_right':
                x = tickline.line_pos + self.line_offset
            else:
                x = tickline.right - th
            y = tick_pos
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
                y = tickline.line_pos + self.line_offset
            elif valign == 'line_bottom':
                y = tickline.line_pos - (th + self.line_offset)
            else:
                y = tickline.y
            x = tick_pos
            width, height = tw, th
            if not return_only:
                self._vertices.extend([x, y, 0, 0,
                                       x + width, y, 0, 0,
                                       x + width, y + height, 0, 0,
                                       x, y + height, 0, 0,
                                       x, y, 0, 0,
                                       x + width, y, 0, 0])

        tick_rect = (x, y, width, height)
        # tickline.labeller.register(self, record_index, tick_rect)  # TODO: Figure out what is wrong here.

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


class TaskTimeLine(Timeline, Themeable):
    def __init__(self, container, **kw):
        super(TaskTimeLine, self).__init__(**kw)
        self.bind(time_0=self._timeline_display_change)
        self.container = container

    def theme_update(self):
        self.line_color = self.theme.text
        self.redraw()

    def _timeline_display_change(self, *args):
        self.container.display_time_start = self.time_0
        self.container.display_time_end = self.time_1


    # Todo: Tie scale to a slider.
