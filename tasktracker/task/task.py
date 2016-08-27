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

from tasktracker.database.db_interface import db
from tasktracker.themes import themes
from tasktracker.themes.themes import __Theme__
import tasktracker.task.taskpopups

# Todo: Task widget should be able to be clicked and opens up a editing screen.
# Todo: Task widget should be able to be categorized in larger project groupings.

_project_shadow_color = [0, 0, 0, .5]


class Task(Button):
    """ Contains all controller information for the task objects. Visual layout is contained in
    task.kv file that is in ./layouts. Note that due to how the label dynamic layout works all
    label attribute access should go through self.tasktext
    """

    task_color = ListProperty(__Theme__.tasks)
    current_project_color = ListProperty()
    current_shadow_color = ListProperty()
    current_project_shadow_color = ListProperty()
    task_texture = StringProperty(themes.__task_texture__)
    shadow_texture = StringProperty(themes.__shadow__)
    project_indicator = StringProperty(themes.__project_indicator__)
    project = ObjectProperty(None)

    def __init__(self, id, name, notes, project_id=0, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.drop_type = 'task'
        self.uuid = id

        # Init self.tasktext
        self.tasktext = Label()
        self.add_widget(self.tasktext)
        self.tasktext.text = name

        self.tasktext.color = [0, 0, 0, 1]  # Todo: replace this with theme data.
        # self.tasktext.disabled_color = [0, 0, 0, .38]  # Todo: replace this with theme data.
        # self.tasktext.font_size = 17

        self.tasktext.halign = 'left'
        self.tasktext.valign = 'middle'
        self.tasktext.shorten_from = 'right'
        self.bind(size=self._label_position_update)
        self.bind(pos=self._label_position_update)

        if project_id != 0:
            self.project = tasktracker.task.taskpopups.__projects__.return_project_by_id(project_id)
        self._update_project_display(self, self.project)

        self.bind(project=self._update_project_display)

        # TODO: Adjust label to global positioning

        self.notes = notes
        # Used For Click Drag Movement
        self.last_parent = None
        self.last_index = None

        self.x_off = self.x
        self.y_off = self.y

    def set_text(self, text):
        self.tasktext.text = text

    def _update_project_display(self, task, project):
        if project is None:
            self.current_project_color = themes.__transparent__  # Make the project rectangle transparent
            self.current_project_shadow_color = themes.__transparent__
        elif project.name == 'No Project':
            self.current_project_color = themes.__transparent__  # Make the project rectangle transparent
            self.current_project_shadow_color = themes.__transparent__
            self.project = None

        else:
            self.project = project
            self.current_project_color = get_color_from_hex(project.color)
            self.current_project_shadow_color = _project_shadow_color

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

    def on_touch_down(self, touch):
        # TODO: Figure out how right click works!
        # TODO: Figure out how time based clicking works.
        # TODO: Figure out a better way to trigger click drag rearrangements

        if self.collide_point(*touch.pos):
            __Theme__.set_theme('Dark Theme')
            tvc = self.get_root_window().children[0]
            self.state = 'down'
            self.x_off = touch.x - self.x
            self.y_off = touch.y - self.y
            self.last_index = self.parent.children.index(self)
            self.last_parent = self.parent  # Used to handle if mouse is outside window boundaries
            global_pos = self.to_window(touch.x, touch.y)
            global_pos = global_pos[0] - self.x_off, global_pos[1] - self.y_off  # Offset Global POS
            tvc.click_drag_reposition(self, tuple(self.size), global_pos)
            touch.grab(self)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.state = 'normal'
            col_data = self.parent.check_children(touch.pos, self)
            self.parent.remove_widget(self)
            self.size_hint_x = 1
            last_list = self.last_parent
            if col_data[0] is not None:  # If it is None then task was released outside of a TaskList..
                self.last_parent = col_data[0]
            if col_data[1]:
                in_index = col_data[1].parent.children.index(col_data[1])
                self.last_parent.add_widget(self, index=in_index + 1)
            else:
                self.last_parent.add_widget(self)
            db.task_switch(self.uuid, self.last_parent.list_id)
            last_list.update_list_positions()  # Writes new indexs to database from list that task left
            self.last_parent.update_list_positions()  # writes new task indexes to the database

            touch.ungrab(self)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.pos = (touch.x - self.x_off, touch.y - self.y_off)
            # print(touch.pos)
            # self.parent.switch_positions(self)
