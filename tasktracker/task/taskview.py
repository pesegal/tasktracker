from kivy.animation import Animation
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from tasktracker.task.taskcontainer import TaskScrollContainer

from tasktracker.mixins import Broadcast
from tasktracker.database.db_interface import DB
from tasktracker.task.task import Task
from tasktracker.settings.settingscontroller import APP_CONTROL


class TaskListView(FloatLayout, Broadcast):
    """
        This class dynamically displays different scroll views based on how many
        widgets are supplied during construction this is used in conjunction with
        the task list view controller to provide changing views with window resize.

        This class also contains all the scrolling animation coding.
    """
    def __init__(self, widget, **kwargs):
        super(TaskListView, self).__init__(**kwargs)
        self.add_widget(widget)
        self.width_hint = 0

    def swap_single_widget(self, new_widget, direction='right'):
        dur = .2
        animation_type = 'out_expo'
        new_widget.size_hint_x = self.width_hint
        if new_widget in self.children:
            self.remove_widget(new_widget)

        if direction is 'right':
            new_widget.x = self.width
            self.add_widget(new_widget)

            widget_width = self.width * self.width_hint
            animation_list = []
            widget_list = []

            for child in reversed(self.children):
                widget_list.append(child)
                animation_list.append(Animation(pos=(child.x - widget_width, child.y),
                                                duration=dur, t=animation_type))
            animation_list[0].bind(on_complete=self.animation_list_remover)

            for i, animation in enumerate(animation_list):
                widget_list[i].pos_hint = {}
                animation.start(widget_list[i])

        if direction is 'left':
            new_widget.x = self.x - (self.width * self.width_hint)
            self.add_widget(new_widget, index=len(self.children))
            widget_width = self.width * self.width_hint
            animation_list = []
            widget_list = []

            for child in self.children:
                widget_list.append(child)
                animation_list.append(Animation(pos=(child.x + widget_width, child.y),
                                                duration=dur, t=animation_type))
            animation_list[0].bind(on_complete=self.animation_list_remover)

            for i, animation in enumerate(animation_list):
                widget_list[i].pos_hint = {}
                animation.start(widget_list[i])

    def animation_list_remover(self, animation, widget):
        self.remove_widget(widget)
        i = 0   # This resets childrens position hints.
        for child in reversed(self.children):
            child.pos_hint = {'x': i / len(self.children)}
            i += 1
        self.broadcast_parent('_animation_complete')

    def view_change(self, widgets):
        self.clear_widgets()
        i = 0
        self.width_hint = 1 / len(widgets)
        for widget in widgets:
            widget.size_hint_x = self.width_hint
            widget.pos_hint = {'x': i / len(widgets)}
            self.add_widget(widget)
            i += 1


class TaskListScreen(Screen, Broadcast):
    """
        This is the task screen that contains references to all the list objects. And contains the logic for
        changing the task list view.
    """
    def __init__(self, **kwargs):
        super(TaskListScreen, self).__init__(**kwargs)
        self.today_list = TaskScrollContainer(list_id=0, name='today')
        self.tomorrow_list = TaskScrollContainer(list_id=1, name='tomorrow')
        self.future_list = TaskScrollContainer(list_id=2, name='future')
        self.archived_list = TaskScrollContainer(list_id=3, name='archived')
        self.deleted_list = TaskScrollContainer(list_id=4, name='deleted')

        # current size of screen
        self.width_state = 0

        # Register reference in app control singleton
        APP_CONTROL.task_list_screen = self

        self.current_display = TaskListView(self.today_list)
        self.add_widget(self.current_display)

        # used in list swapping
        self.lists = [self.today_list, self.tomorrow_list, self.future_list, self.archived_list]
        self.list_slide_queue = []
        self.animating = False
        self.lists_pos = 0

        self.current_touch_pos = None

        # Init loading tasks from database
        DB.load_all_tasks(self._tasks_loaded)

    def _tasks_loaded(self, loaded_tasks, dt):
        for record in loaded_tasks:
            self.add_task_to_list(Task(record[0], record[6], record[7], record[3]), record[4] - 1)

    def add_task_to_list(self, task, list_id):
        list_index = self.get_list_length(list_id)  # Adds to the top instead of the bottom.
        if list_id == 0:
            self.today_list.task_list.add_widget(task, index=list_index)
        elif list_id == 1:
            self.tomorrow_list.task_list.add_widget(task, index=list_index)
        elif list_id == 2:
            self.future_list.task_list.add_widget(task, index=list_index)
        elif list_id == 3:
            self.archived_list.task_list.add_widget(task, index=list_index)
        elif list_id == 4:
            self.deleted_list.task_list.add_widget(task)  # TODO: sort deleted tasks?

    def get_list_length(self, list_id):
        if list_id == 0:
            return len(self.today_list.task_list.children)
        elif list_id == 1:
            return len(self.tomorrow_list.task_list.children)
        elif list_id == 2:
            return len(self.future_list.task_list.children)
        elif list_id == 3:
            return len(self.archived_list.task_list.children)

    def width_state_change(self, **kwargs):
        # This function changes the display based on the width_state of the screen
        state = kwargs['width_state']
        self.width_state = state
        if state == 0 or state == 1:
            self.current_display.view_change([self.today_list])
        elif state == 2:
            self.current_display.view_change([self.today_list, self.tomorrow_list])
            self.current_display.view_change([self.today_list, self.tomorrow_list])
        elif state == 3:
            self.current_display.view_change([self.today_list, self.tomorrow_list, self.future_list])
        elif state == 4:
            self.current_display.view_change([self.today_list, self.tomorrow_list,
                                              self.future_list, self.archived_list])
        self.lists_pos = 0

    def slide_task_lists(self, **kwargs):
        self.list_slide_queue.append(kwargs['direction'])
        if not self.animating:
            self._slide_lists()

    def _animation_complete(self):
        self.animating = False
        if self.list_slide_queue:
            self._slide_lists()

    def _slide_lists(self):
        self.animating = True
        direction = self.list_slide_queue.pop()
        list_length = len(self.lists) - 1
        if self.width_state == 0 or self.width_state == 1:
            if direction is 'right' and self.lists_pos < list_length:
                self.current_display.swap_single_widget(self.lists[self.lists_pos + 1], direction)
                self.lists_pos += 1
            elif direction is 'left' and self.lists_pos > 0:
                self.current_display.swap_single_widget(self.lists[self.lists_pos - 1], direction)
                self.lists_pos -= 1
            else:
                self.animating = False
        elif self.width_state == 2:
            if direction is 'right' and self.lists_pos + 1 < list_length:
                self.current_display.swap_single_widget(self.lists[self.lists_pos + 2], direction)
                self.lists_pos += 1
            elif direction is 'left' and self.lists_pos > 0:
                self.current_display.swap_single_widget(self.lists[self.lists_pos - 1], direction)
                self.lists_pos -= 1
            else:
                self.animating = False
        elif self.width_state == 3:
            if direction is 'right' and self.lists_pos + 2 < list_length:
                self.current_display.swap_single_widget(self.lists[self.lists_pos + 3], direction)
                self.lists_pos += 1
            elif direction is 'left' and self.lists_pos > 0:
                self.current_display.swap_single_widget(self.lists[self.lists_pos - 1], direction)
                self.lists_pos -= 1
            else:
                self.animating = False
        else:
            self.animating = False
