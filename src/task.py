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
import uuid
from kivy.uix.button import Button
from kivy.graphics import Rectangle


# Todo: Create the basic task widget that contains task title information.
# Todo: Task widget should be able to be clicked and opens up a editing screen.
# Todo: Task widget should be able to be categorized in larger project groupings.
# Todo: Categorized tasks should have a colorized marker on their graphical representation that shows grouping.
# Todo: Task widget should track statistical information based on user interaction.


class Task(Button):
    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.uuid = uuid.uuid1()

        self.x_off = self.x
        self.y_off = self.y

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            tvc = self.parent.parent.parent.parent
            self.state = 'down'
            self.x_off = touch.x - self.x
            self.y_off = touch.y - self.y

            print(self.get_root_window())

            tvc.click_drag_reposition(self)
            touch.grab(self)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            print("Ungrabbing: %s" % self.uuid.hex )
            self.state = 'normal'

            # Todo: Look into improving the positioning in the list!
            widget_list = self.parent.check_children(touch.pos)
            self.parent.remove_widget(self)
            widget_list.add_widget(self)


            touch.ungrab(self)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and touch.grab_current is self:
            self.pos = (touch.x - self.x_off, touch.y - self.y_off)

            # self.parent.switch_positions(self)






