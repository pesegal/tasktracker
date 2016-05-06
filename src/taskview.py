from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from src.taskcontainer import TaskScrollContainer
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.animation import Animation
from kivy.lang import Builder
from src.broadcast import BroadcastMixin

Builder.load_file('./src/taskview.kv')


class TaskListView(FloatLayout, BroadcastMixin):
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
        print("ANIMATING")
        new_widget.size_hint_x = self.width_hint

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
                print(animation, widget_list[i])
                widget_list[i].pos_hint = {}
                animation.start(widget_list[i])

        if direction is 'left':
            new_widget.x = self.x - self.width
            self.add_widget(new_widget, 0)

            widget_width = self.width * self.width_hint
            animation_list = []
            widget_list = []

            for child in self.children:
                widget_list.append(child)
                animation_list.append(Animation(pos=(child.x + widget_width, child.y),
                                                duration=dur, t=animation_type))
            animation_list[-1].bind(on_complete=self.animation_list_remover)
            for i, animation in enumerate(animation_list):
                print(animation, widget_list[i])
                widget_list[i].pos_hint = {}
                animation.start(widget_list[i])

    def animation_list_remover(self, animation, widget):
        print('Animation complete removing : %s' % widget.uid)
        self.remove_widget(widget)
        i = 0   # This resets childrens position hints.
        for child in reversed(self.children):
            child.pos_hint = {'x': i / len(self.children)}

    def view_change(self, widgets):
        child_list = tuple(self.children)
        for child in child_list:
            self.remove_widget(child)
        i = 0
        self.width_hint = 1 / len(widgets)
        for widget in widgets:
            widget.size_hint_x = self.width_hint
            widget.pos_hint = {'x': i / len(widgets)}
            self.add_widget(widget)
            i += 1


class TaskListScreen(Screen, BroadcastMixin):
    """
        This is the task screen that contains references to all the list objects. And contains the logic for
        changing the task list view.
    """
    def __init__(self, **kwargs):
        super(TaskListScreen, self).__init__(**kwargs)
        self.today_list = TaskScrollContainer()
        self.tomorrow_list = TaskScrollContainer()
        self.future_list = TaskScrollContainer()
        self.archived = TaskScrollContainer()

        # current size of screen
        self.width_state = 0

        self.current_display = TaskListView(self.today_list)
        self.add_widget(self.current_display)

        # used in list swapping
        self.lists = [self.today_list, self.tomorrow_list, self.future_list, self.archived]
        self.lists_pos = 0


        self.current_touch_pos = None

    def width_state_change(self, **kwargs):
        state = kwargs['width_state']
        self.width_state = state
        if state == 0 or state == 1:
            self.current_display.view_change([self.today_list])
        elif state == 2:
            self.current_display.view_change([self.today_list, self.tomorrow_list])
        elif state == 3:
            self.current_display.view_change([self.today_list, self.tomorrow_list, self.future_list])
        elif state == 4:
            self.current_display.view_change([self.today_list, self.tomorrow_list,
                                              self.future_list, self.archived])

    def ani_test(self, select):
        if self.width_state == 0 or self.width_state == 1:
            if select is 'right' and self.lists_pos < len(self.lists) - 1:
                self.current_display.swap_single_widget(self.lists[self.lists_pos + 1], select)
                self.lists_pos += 1
            elif select is 'left' and self.lists_pos > 0:
                self.current_display.swap_single_widget(self.lists[self.lists_pos - 1], select)
                self.lists_pos -= 1

    def click_drag_reposition(self, task, size, position):
        task.parent.remove_widget(task)
        self.add_widget(task)
        task.pos = position
        task.size_hint_x = None
        task.size = size

    def check_children(self, touch_pos):
        """
        This function returns the task list widget and the task widget the touch position releases on.
        :param touch_pos:
        :return: TaskList Widget, Task Object
        """
        # TODO Will need to add a check in case it's not a scroll view.
        t_list = None
        task = None

        for child in self.children:
            if not child.collide_point(*touch_pos):
                continue
            for c in child.children:
                if c.collide_point(*touch_pos):
                    t_list = c.task_list
            if not t_list:
                continue
            for tasks in t_list.children:
                if tasks.collide_point(*tasks.to_widget(*touch_pos)):
                    task = tasks
        return t_list, task