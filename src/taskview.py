from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from src.taskcontainer import TaskScrollContainer
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.animation import Animation
from kivy.lang import Builder

Builder.load_file('./src/taskview.kv')


class TaskListView(FloatLayout):
    """
       This class dynamically displays different scroll views based on how many
        widgets are supplied during construction this is used in conjunction with
        the task list view controller to provide changing views with window resize.
    """
    def __init__(self, widget, **kwargs):
        super(TaskListView, self).__init__(**kwargs)
        self.add_widget(widget)

    def swap_single_widget(self, current_widget, new_widget, direction='right'):
        dur = .3
        animation_type = 'in_out_quad'
        print("ANIMATING")
        self.add_widget(new_widget)

        if direction is 'right':
            new_widget.pos = (self.right, self.y)
            wid_out = Animation(pos=(-current_widget.width, current_widget.y), duration=dur, t=animation_type)
            wid_in = Animation(pos=(self.x, self.y), duration=dur, t=animation_type)

            wid_out.start(current_widget)
            wid_in.start(new_widget)
            wid_out.on_complete(self.remove_widget(current_widget))

        if direction is 'left':
            new_widget.pos = (-self.right, self.y)
            wid_out = Animation(pos=(current_widget.width, current_widget.y), duration=dur, t=animation_type)
            wid_in = Animation(pos=(self.x, self.y), duration=dur, t=animation_type)

            wid_out.start(current_widget)
            wid_in.start(new_widget)
            wid_out.on_complete(self.remove_widget(current_widget))

            # TODO: FIGURE OUT HOW TO GET THE WIDGETS TO REMOVE AFTER THE ANIMATION IS COMPLETED

    def view_change(self, widgets):
        child_list = tuple(self.children)
        for child in child_list:
            self.remove_widget(child)

        for widget in widgets:
            self.add_widget(widget)


class TaskListScreen(Screen):
    def __init__(self, **kwargs):
        super(TaskListScreen, self).__init__(**kwargs)
        self.today_list = TaskScrollContainer()
        self.tomorrow_list = TaskScrollContainer()
        self.future_list = TaskScrollContainer()
        self.archived = TaskScrollContainer()

        self.current_display = TaskListView(self.today_list)
        self.add_widget(self.current_display)

        self.current_touch_pos = None

    def ani_test(self, select):
        if select is 'right':
            self.current_display.swap_single_widget(self.today_list, self.tomorrow_list, select)
        else:
            self.current_display.swap_single_widget(self.tomorrow_list, self.today_list, select)

    def screen_resize(self, *args):
        if args[1][0] < 640:
            self.current_display.view_change([self.today_list])
        elif 640 < args[1][0] < 960:
            self.current_display.view_change([self.today_list, self.tomorrow_list])
        elif 960 < args[1][0]:
            self.current_display.view_change([self.today_list, self.tomorrow_list, self.future_list])

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