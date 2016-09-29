from kivy.properties import NumericProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import FallOutTransition, SlideTransition,\
    SwapTransition, FadeTransition, WipeTransition, RiseInTransition
from kivy.clock import Clock


from tasktracker.mixins import Broadcast
from tasktracker.menubar import MenuBar
from tasktracker.task.taskview import TaskListScreen
from tasktracker.task.taskpopups import TaskEditScreen
from tasktracker.timer.timer import TimerScreen
from tasktracker.themes.themes import Themeable
from tasktracker.task.clickdragcontrol import CLICK_DRAG_CONTROLLER


class ScreenController(ScreenManager, Broadcast, Themeable):
    def __init__(self, **kwargs):
        super(ScreenController, self).__init__(**kwargs)

        self.tasks = TaskListScreen(name='tasks')
        self.timer = TimerScreen(name='timer')
        self.stats = StatsScreen(name='stats')
        self.theme_update()

        self.add_widget(self.tasks)
        self.add_widget(self.timer)
        self.add_widget(self.stats)

    def theme_update(self):
        self.transition = WipeTransition()
        self.transition.clearcolor = self.theme.background
        self.transition.duration = .08


class StatsScreen(Screen): # TODO: Break this out into it's own module eventually.
    pass


class ScreenMenuAndDisplay(BoxLayout, Broadcast):
    screen_size = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ScreenMenuAndDisplay, self).__init__(**kwargs)
        self.orientation = 'vertical'
        # This will list all the different sub-screens
        self.bind(size=self.screen_width_state)
        self.screen_controller = ScreenController()
        self.menu_bar = MenuBar()

        # This is where you transmit
        self.bind(screen_size=self.broadcast_window_resize)

        self.add_widget(self.menu_bar)
        self.add_widget(self.screen_controller)

    def screen_width_state(self, *args):
        if args[1][0] < 360:  # Small width screens where text needs to be icons
            self.screen_size = 0
        elif 360 < args[1][0] < 640:  # Single list
            self.screen_size = 1
        elif 640 < args[1][0] < 960:
            self.screen_size = 2
        elif 960 < args[1][0] < 1280:
            self.screen_size = 3
        elif 1280 < args[1][0]:
            self.screen_size = 4

    def broadcast_window_resize(self, *args):
        # print(self.screen_size, "ARGS: ", args)
        self.broadcast_child('width_state_change', width_state=self.screen_size)


class ScreenClickDragWindow(FloatLayout, Broadcast):
    def __init__(self, **kwargs):
        super(ScreenClickDragWindow, self).__init__(**kwargs)
        self.screen_menu = ScreenMenuAndDisplay()
        self.add_widget(self.screen_menu)
        self.direction = 'left'
        self._event = None
        CLICK_DRAG_CONTROLLER.click_drag_window = self  # create reference in the controller

        # Label
        self.task_list_screen = self.screen_menu.screen_controller.tasks
        self.labels = list()

    def display_list_names(self):
        for list in self.task_list_screen.lists:
            list.label_view.show_label()

    def remove_list_names(self):
        for list in self.task_list_screen.lists:
            list.label_view.remove_label()

    def click_drag_reposition(self, task, size, position):
        task.parent.remove_widget(task)
        self.add_widget(task)
        self.screen_menu.menu_bar.start_drag_menu_button_text()
        task.pos = position
        task.size_hint_x = None
        task.size = size
        self.display_list_names()

    def drag_scroll_check(self, touch_pos):
        """ This function triggers the switching of lists when a task object is moved with in
        5 pixels of the edge of the screen.
        :param touch_pos: the x y position of the current touch translated to global pos.
        """
        _list_drag_time = .2

        if touch_pos[0] > self.width - 5:
            self.direction = 'right'
            if self._event is None:
                self._event = Clock.schedule_once(self._broadcast_list_switch, _list_drag_time)
        elif touch_pos[0] < 5:
            self.direction = 'left'
            if self._event is None:
                self._event = Clock.schedule_once(self._broadcast_list_switch, _list_drag_time)
        else:
            if self._event is not None:
                self._event.release()  # stop any outstanding events
            self._event = None

    def _broadcast_list_switch(self, *args):
        self.broadcast_child('slide_task_lists', direction=self.direction)
        self._event = None

    def check_children(self, touch_pos, selected_task):
        """
        This function returns the task list widget and the task widget the touch position releases on.
        :param touch_pos: tuple of the x, y position of the current touch
        :param selected_task: instance of the selected task widget
        :return: TaskList, Task
        """
        t_list = None
        task = None

        widget_list = []

        for widget in self.walk():  # Todo Try setting to true?
            widget_list.append(widget)
            if widget in self.children:  # Skip currently selected task.
                continue
            drop = hasattr(widget, 'drop_type')
            if widget.collide_point(*touch_pos) and drop:  # check for task_list collision
                if widget.drop_type == 'scroll_list':
                    t_list = widget.task_list
                elif widget.drop_type == 'task_edit':
                    TaskEditScreen(selected_task).open()
                elif widget.drop_type == 'timer':
                    self.screen_menu.screen_controller.timer.ids.task_manager.load_task(selected_task)
                    self.screen_menu.menu_bar.current_screen = 'timer'
                    self.screen_menu.screen_controller.current = 'timer'
                elif widget.drop_type == 'settings':
                    t_list = self.screen_menu.screen_controller.tasks.deleted_list.task_list

            if widget.collide_point(*widget.to_widget(*touch_pos)) and drop:  # test for task collision
                if widget.drop_type == 'task':
                    task = widget

        self.remove_list_names()
        self.screen_menu.menu_bar.release_drag_menu_button_text()
        return t_list, task





