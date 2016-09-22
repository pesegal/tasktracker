from tasktracker.settings import Borg
from tasktracker.database.db_interface import DB

from kivy.animation import Animation


class ClickDragController(Borg):
    """ This controller object is the better way of handling click drag related functionality.
        On program start the ScreenClickDragWindow registers itself with this class.
        when a task for is triggered for click drag it registers itself also.
    """
    def __init__(self):
        super().__init__()
        self.click_drag_window = None
        self.drop_list = []

        # Popup expansion amount
        self.width_exp = 10
        self.height_exp = 10

        # Task Click Drag Movement
        self.height = None
        self.last_parent = None
        self.last_index = None

    def start_click_drag(self, task, touch):
        # task.state = 'down'
        task.x_off = touch.x - task.x
        task.y_off = touch.y - task.y
        self.last_index = task.parent.children.index(task)
        self.last_parent = task.parent  # Used to handle if mouse is outside window boundaries
        global_pos = task.to_window(touch.x, touch.y)
        global_pos = global_pos[0] - task.x_off, global_pos[1] - task.y_off  # Offset Global POS
        self.height = task.height
        popup = Animation(size=(task.width + self.width_exp, task.height + self.height_exp),
                          duration=.1, t='in_back')
        popup.start(task)
        self.click_drag_window.click_drag_reposition(task, tuple(task.size), global_pos)
        touch.grab(task)

    def stop_click_drag(self, task, touch):
        # task.state = 'normal'
        col_data = self.click_drag_window.check_children(touch.pos, task)
        self.click_drag_window.remove_widget(task)
        task.size_hint_x = 1
        last_list = self.last_parent
        task.height = self.height
        if col_data[0] is not None:  # If it is None then task was released outside of a TaskList..
            self.last_parent = col_data[0]
        if col_data[1]:
            in_index = col_data[1].parent.children.index(col_data[1])
            self.last_parent.add_widget(task, index=in_index + 1)
        else:
            self.last_parent.add_widget(task)
        if self.last_parent != last_list:  # Only record the task list switch if it's a different list.
            DB.task_switch(task.uuid, self.last_parent.list_id)
        last_list.update_list_positions()  # Writes new index to database from list that task left
        self.last_parent.update_list_positions()  # writes new task indexes to the database
        touch.ungrab(task)

    # TODO: Improve dropping check to reduce walking of child widgets.

CLICK_DRAG_CONTROLLER = ClickDragController()