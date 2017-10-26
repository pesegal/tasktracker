from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, StringProperty
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout

from copy import copy
from tasktracker.database.db_interface import DB
from tasktracker.stats.timeline import TaskTimeLine, VisualTimeTick, PeriodDisplayTick, RecordPeriod
from tasktracker.stats.datecontrols import StatsTimeSelectionMenu
from tasktracker.settings.settingscontroller import DataContainer, to_datetime, to_local_time
from datetime import datetime, timezone, timedelta
from tasktracker.task.taskpopups import PROJECT_LIST
from tasktracker.themes.themes import THEME_CONTROLLER, Themeable
from tasktracker.themes import themes
from tasktracker.stats.datecontrols import ErrorNotificationPopup, SliderNotificationPopup
from functools import partial
from collections import namedtuple, Counter

# TODO: DEFAULT COLORS FOR SHORT BREAK, LONG BREAK, & PAUSE (MAKE THESE CONFIGURABLE IN SETTINGS?)

# Todo: write a helper function that takes start and end datetimes and returns the number of months, weeks, days


class StandardStatsScreen(Screen):
    """ The standard stats screen view contains the project / task summary screen and the timeline
    view.
    """

    def __init__(self, **kwargs):
        super(StandardStatsScreen, self).__init__(**kwargs)


class TaskProjectStatsSummaryView(BoxLayout, Themeable):
    """ Contains all the updating logic for the task/project summary view. This statical view lists
    all of the tasks or projects withing the specified time frame that can be sorted by taskname,
    work time, or break time. It also calculates totals (worktime, breaktime)
     for all tasks or projects in selected time period.
    """

    def __init__(self, **kwargs):
        super(TaskProjectStatsSummaryView, self).__init__(**kwargs)

    def theme_update(self):
        pass


class RecordDetailGridView(GridLayout):
    def __init__(self, **kwargs):
        super(RecordDetailGridView, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))


class TimelineContainer(RelativeLayout):
    """ TimelineContainer object contains all functionality related to the display and manipulation
        of the timeline.
    """

    display_time_start = ObjectProperty(None)
    display_time_end = ObjectProperty(None)
    timeline_zoom_slider = ObjectProperty(None)
    timeline = ObjectProperty()

    label_start = ObjectProperty()
    label_end = ObjectProperty()

    # Timeline Zoom State
    zoom_state = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Error notification popup variables
        self.error_popup = None
        self.bind(on_size=self.error_popup_reposition, on_pos=self.error_popup_reposition)
        self.bind(zoom_state=self._zoom_state_update)

        # Slider notification popup variables
        self.slider_popup = None
        self.slider_call_counter = 0

        # self.bind(display_time_start=self._display_time_update)
        # self.bind(display_time_end=self._display_time_update)
        # TODO: Figure out a better way to display time ticks based on scale.
        self.time_ticks = [VisualTimeTick(mode=VisualTimeTick.mode.options[i], valign='line_bottom') for i in
                           [0, 2, 5, 6, 7, 9, 10]]
        self.time_ticks.extend([VisualTimeTick(mode=VisualTimeTick.mode.options[i], valign='line_top',
                                               tick_color=[1, 1, 1, 1]) for i in [0, 2, 5, 6, 7, 9, 10]])

        today = datetime.now(tz=timezone.utc)
        t_buffer = timedelta(days=60)

        # TODO: Figure out what would be the best starting period.
        self.display_time_start = datetime(year=today.year, month=today.month, day=today.day,
                                           hour=0, minute=0, tzinfo=timezone.utc)
        self.display_time_end = datetime(year=today.year, month=today.month, day=today.day,
                                         hour=23, minute=0, tzinfo=timezone.utc)

        DB.load_task_actions(self.display_time_start - t_buffer,
                             self.display_time_end + t_buffer, self._display_timeline)
        print(self.ids)

    def _zoom_state_update(self, *args):
        print("zoom_state updated", args)

    def open_dt_selection_menu(self, dt, label):
        self.add_widget(StatsTimeSelectionMenu(dt, label, self.timeline))

    def touch_label_check(self, touch):
        """ Checks if the touch is within any of the areas to keep the StatsTimeSelectionMenu
        object open. Allow the user to open both time selection menus at the same time.

        :return True if the touch is in any of the proper areas
        """
        if self.label_start.bubble_selection_menu:
            if self.label_start.bubble_selection_menu.collide_point(touch.x, touch.y):
                return True
        if self.label_end.bubble_selection_menu:
            if self.label_end.bubble_selection_menu.collide_point(touch.x, touch.y):
                return True
        if self.label_start.collide_point(touch.x, touch.y):
            return True
        if self.label_end.collide_point(touch.x, touch.y):
            return True
        return False

    def open_error_notification_popup(self, message):
        self.error_popup = ErrorNotificationPopup(message)
        err_original_size = copy(self.error_popup.size)
        self.error_popup.size = (self.error_popup.width / 1.7, self.error_popup.height / 2)
        print(err_original_size, self.error_popup.size)
        err_animation = Animation(size=err_original_size,
                                  duration=.2, t='out_cubic')
        self.add_widget(self.error_popup)
        err_animation.start(self.error_popup)

    def error_popup_reposition(self, *args):
        if self.error_popup:
            self.error_popup.pos = 400, 200

    def _update_slider_popup_position(self, anim, popup):
        popup.center_x = self.timeline_zoom_slider.get_value_pos()[0]

    def update_slider_notification_popup(self, slider, message):
        if not self.slider_popup:
            self.slider_popup = SliderNotificationPopup(message)

            slider_original_size = copy(self.slider_popup.size)
            self.opacity = 0
            self.slider_popup.y = slider.height
            self.add_widget(self.slider_popup)
            # Schedule the positing on the next frame so that positing will work correctly.
            Clock.schedule_once(partial(self._popup_init_pos_callback,
                                        slider.get_value_pos()[0],
                                        slider.height,
                                        slider_original_size))

        else:
            self.slider_popup.set_message(message)
            self.slider_popup.center_x = slider.get_value_pos()[0]
            self.slider_popup.y = slider.height

    def _popup_init_pos_callback(self, x_pos, y_pos, slider_original_size, *largs):
        self.slider_popup.center_x = x_pos
        self.slider_popup.y = y_pos
        self.slider_popup.size = (self.slider_popup.width, self.slider_popup.height / 2)
        self.opacity = 1
        slider_animation = Animation(size=slider_original_size, opacity=1,
                                     duration=.2, t='out_cubic')
        slider_animation.start(self.slider_popup)

    def close_slider_notification_popup(self):
        if self.slider_popup:
            slider_animation = Animation(size=(self.slider_popup.width, 0), opacity=0,
                                         duration=.2, t='in_cubic')
            slider_animation.bind(on_complete=self._close_slider_complete_callback)
            slider_animation.start(self.slider_popup)
            self.slider_popup = None

    def _close_slider_complete_callback(self, anim, slider):
        self.remove_widget(slider)

    def _display_timeline(self, data, tb):
        """ Temporary timeline display method.

        :param data:
        :param tb:
        :return:
        """

        # TODO: How many years, months, days, hours and minutes are currently displayed at current scale

        # TODO: Chose the best way to display the data, timeline layout or proportional bar graph.

        # TODO: Allow for filtering on project type, ect.

        # TODO: use factory pattern to properly return the display object list.

        # TODO: Standard Timeline Display
        """ Standard Timeline Display Features
            - Display as selected by project color and pause break.
            - Clicking on a project will bring up that tasks information.
            - Display the summary for the entire period.
        """

        # TODO: Proportion Bar Graph:
        """ Proportional Bar Graph Features
            - Take a proportion of the height above the line and use that as the max height.
            - Set the period with the most records to the max height.
            - All other records are proportionally related to the record with the max height.
            - Draw the different records stacked by project color.
            - If the section is clicked on the pop-up will display totals for that day.
            - Take the same except below the line for pauses and breaks.
        """

        # TODO: Split Records by Project Type and Action Type
        project_dict = dict()

        for item in data:
            record = RecordPeriod(*item)

            if record.project_id in project_dict.keys():
                if record.action_type in project_dict[record.project_id].keys():
                    project_dict[record.project_id][record.action_type].append(record)
                else:
                    project_dict[record.project_id][record.action_type] = [record]
            else:
                project_dict[record.project_id] = {record.action_type: [record]}

        for key, value in project_dict.items():

            # Get Project Color Else Default
            project = PROJECT_LIST.return_project_by_id(key)
            if project.color is None:
                p_color = THEME_CONTROLLER.selected
            else:
                p_color = get_color_from_hex(project.color)

            p_color[3] = .7  # Add some transparency to the timeline.

            for t_key, t_value in value.items():
                if t_key == 2:  # if type is pomodoro
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


class StatsDataController(DataContainer):
    """
    StatsDataController handles all of the in memory store of statistical information, loading and clearing
    of this statistical information from the database. It also contains the logic that slices and sums this
    data for the different statistical views.
    """
    def __init__(self, **kwargs):
        super(StatsDataController, self).__init__(**kwargs)
        self.load_data()
        self.StatRecord = namedtuple('StatRecord',
                                     ['action_id', 'creation_date', 'finish_date', 'duration',
                                      'type', 'task_id', 'task_name', 'project_id', 'project_name'])
        self.stats_data = list()

        # Testing Code
        self.test_time_period = [to_local_time(datetime.now(timezone.utc)) - timedelta(days=20),
                                 to_local_time(datetime.now(timezone.utc))]

    def clear_data(self):
        self.stats_data = list()

    def load_data(self, min_time=datetime.min, max_time=datetime.max):
        DB.get_task_actions_stats(min_time, max_time, self._stats_data_loaded)

    def _stats_data_loaded(self, data, *args):
        self.stats_data = [stat._replace(
            creation_date=to_local_time(to_datetime(stat.creation_date)),
            finish_date=to_local_time(to_datetime(stat.finish_date))
        ) for stat in [self.StatRecord(*rcd) for rcd in data]]

    @staticmethod
    def _in_dt_range(dt_min, dt_max, start_time, end_time):
        return ((dt_max >= start_time >= dt_min) or
                (dt_max >= end_time >= dt_min))

    def _return_records_in_daterange(self, time_period):
        if time_period:
            # TODO: local datetime conversion here?
            min_dt = time_period[0]
            max_dt = time_period[1]
        else:
            min_dt = to_local_time(datetime.min)
            max_dt = to_local_time(datetime.max)
        # Filter out only the records in the effective range.
        return [rec for rec in self.stats_data if self._in_dt_range(min_dt, max_dt,
                                                                    rec.creation_date,
                                                                    rec.finish_date)]

    def return_summary_stats(self, group_by='project_id', time_period=None):
        """ Send a start and end time list or tuple. Returns a dict of summed durations in seconds
        keyed by project id.

        :param group_by: element to group by (ex. 'project_id', 'task_id')
        :param time_period: [lower bound datetime, upper bound datetime]
        :return: dict{ project_id: { "WorkTime", "PauseTime", "BreakTime" }}
        """
        records_in_range = self._return_records_in_daterange(time_period)

        stats_dict = dict()
        for record in records_in_range:

            item_id = getattr(record, group_by)

            if item_id not in stats_dict.keys():
                stats_dict[item_id] = dict()
                stats_dict[item_id]['WorkTime'] = 0
                stats_dict[item_id]['PauseTime'] = 0
                stats_dict[item_id]['BreakTime'] = 0

            if record.type == 'Pomodoro' or record.type == 'Stopwatch':
                stats_dict[item_id]['WorkTime'] += record.duration
            elif record.type == 'Pause':
                stats_dict[item_id]['PauseTime'] += record.duration
            else:
                stats_dict[item_id]['BreakTime'] += record.duration

        return stats_dict

    def single_record_stats(self, item_id, item_type='project', time_period=None):
        pass

# Stats View Widgets


class StatsLabel(Label, Themeable):
    def __init__(self, **kwargs):
        super(StatsLabel, self).__init__(**kwargs)

    def theme_update(self):
        pass


class StatsButton(Button, Themeable):
    def __init__(self, **kwargs):
        super(StatsButton, self).__init__(**kwargs)

    def theme_update(self):
        pass


class ProjectTaskDisplay(StatsButton):
    # Themeable Properties
    pt_display_color = ListProperty()
    project_color = ListProperty()
    # Shadow Texture Colors
    shadow_color = ListProperty(themes.SHADOW_COLOR)
    project_shadow_color = ListProperty()
    # Textures
    pt_display_texture = StringProperty(themes.LEFT_BEV_CORNERS)
    pt_display_shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    project_indicator = StringProperty(themes.LEFT_BEV_CORNERS)

    project = ObjectProperty(None)

    def __init__(self, name, project_id=0, **kwargs):
        """

        :param name: The name of the task or project.
        :param project_id:
        :param kwargs:
        """
        super(ProjectTaskDisplay, self).__init__(**kwargs)

        if project_id != 0:
            self.project = PROJECT_LIST.return_project_by_id(project_id)
        self._update_project_display(self, self.project)
        self.bind(project=self._update_project_display)

        # TODO: Finish building loading of names


    def theme_update(self):
        super(ProjectTaskDisplay, self).theme_update()

    def update_project_color(self, color):
        # This function is called by the registered project observer pattern to broadcast all color changes
        self.project_color = color

    def _update_project_display(self, disp, project):
        if project is None:
            self.project_color = themes.TRANSPARENT
            self.project_shadow_color = themes.TRANSPARENT
        elif project.name == 'No Project':
            self.project_color = themes.TRANSPARENT
            self.project_shadow_color = themes.TRANSPARENT
        else:
            self.project = project
            self.project.register(self)
            self.project_color = get_color_from_hex(project.color)
            self.project_shadow_color = themes.SHADOW_COLOR
        self.canvas.ask_update()


class StatsRecordLine(BoxLayout, Themeable):
    """ Each represents a single row in the RecordDetailGridView
        contains all the methods for displaying holding and displaying data returned from
        the StatsDataController
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def theme_update(self):
        pass


###

class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.data_container = StatsDataController()
        self.add_widget(self.sm)

        self.view_timeline = StandardStatsScreen(name='TimelineView')


        self.add_widget(self.view_timeline)
        print(self.sm.screens)




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