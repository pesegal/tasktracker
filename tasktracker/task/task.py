"""
    The task widget class contains all the graphical behavior of a task.

    Statistical tracking todo:
        Date time stamp when created.
        Date time stamp when modified.
        Total time worked on task.
        Number of sessions worked on task.
        Number of pomo's spent on task. << display this as a number of check boxes.
        Number of short breaks spent on task.
        Number of long breaks spent on task.

"""
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.utils import get_color_from_hex

from copy import copy
from kivy.clock import Clock


from tasktracker.themes import themes
from tasktracker.mixins import TapAndHold
from tasktracker.themes.themes import Themeable
from tasktracker.task.clickdragcontrol import CLICK_DRAG_CONTROLLER
import tasktracker.task.taskpopups

# Todo: Task widget should be able to be clicked and opens up a editing screen.
# Todo: Task widget should be able to be categorized in larger project groupings.


class Task(Button, TapAndHold, Themeable):  # TapAndHold
    """ Contains all controller information for the task objects. Visual layout is contained in
    task.kv file that is in ./layouts. Note that due to how the label dynamic layout works all
    label attribute access should go through self.tasktext
    """
    # Themeable Properties
    task_color = ListProperty()
    current_project_color = ListProperty()
    # Shadow Texture Colors: Used for to switch from visible to transparent
    current_shadow_color = ListProperty(themes.SHADOW_COLOR)
    current_project_shadow_color = ListProperty()
    # Task textures
    task_texture = StringProperty(themes.TASK_TEXTURE)
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    project_indicator = StringProperty(themes.PROJECT_TEXTURE)

    project = ObjectProperty(None)

    def __init__(self, id, name, notes, project_id=0, **kwargs):
        super(Task, self).__init__(**kwargs)

        self.drop_type = 'task'
        self.uuid = id

        # Tap Hold Length (Seconds)
        self._hold_length = .5

        # Init self.tasktext
        self.tasktext = Label()
        self.add_widget(self.tasktext)
        self.tasktext.text = name

        self.theme_update()

        self.tasktext.halign = 'left'
        self.tasktext.valign = 'middle'
        self.tasktext.shorten_from = 'right'
        self.bind(size=self._label_position_update)
        self.bind(pos=self._label_position_update)

        if project_id != 0:
            self.project = tasktracker.task.taskpopups.__projects__.return_project_by_id(project_id)
        self._update_project_display(self, self.project)

        self.bind(project=self._update_project_display)
        self.notes = notes

        # Click Drag Variables
        self.x_off = self.x
        self.y_off = self.y

    def theme_update(self):
        self.tasktext.color = self.theme.text
        # self.tasktext.disabled_color = [0, 0, 0, .38] # Figure out how I want to utilize this
        # self.tasktext.font_size = 17
        self.task_color = self.theme.tasks

    def set_text(self, text):
        self.tasktext.text = text

    def _update_project_display(self, task, project):
        if project is None:
            self.current_project_color = themes.TRANSPARENT  # Make the project rectangle transparent
            self.current_project_shadow_color = themes.TRANSPARENT
        elif project.name == 'No Project':
            self.current_project_color = themes.TRANSPARENT  # Make the project rectangle transparent
            self.current_project_shadow_color = themes.TRANSPARENT
        else:
            self.project = project
            self.current_project_color = get_color_from_hex(project.color)
            self.current_project_shadow_color = themes.SHADOW_COLOR
        self.canvas.ask_update()

    def _label_position_update(self, _object, size, short_padding=5):
        start = self.width * .07 + 5
        self.tasktext.width = self.width - start - 20
        self.tasktext.height = self.height
        self.tasktext.text_size = (self.width - start - 40, None)
        # Commented out the section that will turn on self.tasktext shortening.
        # Figure out if the is useful. And how to turn it on and off with fixed height.

        # if not self.tasktext.shorten:
        #     self.multi_line_height = self.tasktext.texture_size[1] + short_padding
        # if (self.tasktext.texture_size[1] + short_padding >= self.height
        #         and not self.tasktext.shorten):
        #     print('TASKS TRUEs')
        #     self.tasktext.shorten = True
        # elif self.multi_line_height < self.height:
        #     self.tasktext.shorten = False
        self.tasktext.x = self.x + start + 5
        self.tasktext.y = self.y

    def on_tap_hold(self, touch):
        CLICK_DRAG_CONTROLLER.start_click_drag(self, touch)

    def on_touch_down(self, touch):
        """ touch down event """
        if self.collide_point(touch.x, touch.y):  # filter touch events
            self.triggered = False
            self._release_event()
            self._point = copy(touch)         # Touch events share an instance
            self._event = Clock.schedule_once(self._long_hold, self._hold_length)

    def on_touch_up(self, touch):
        TapAndHold.on_touch_up(self, touch)
        if touch.grab_current is self and self.triggered:
            CLICK_DRAG_CONTROLLER.stop_click_drag(self, touch)

    def on_touch_move(self, touch):
        TapAndHold.on_touch_move(self, touch)
        if touch.grab_current is self and self.triggered:
            self.pos = (touch.x - self.x_off, touch.y - self.y_off)
            # print(touch.pos)
            # self.parent.switch_positions(self)
