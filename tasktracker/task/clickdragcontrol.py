from tasktracker.settings import Borg


class ClickDragController(Borg):
    """ This controller object is the better way of handling click drag related functionality.
        On program start the ScreenClickDragWindow registers itself with this class.
        when a task for is triggered for click drag it registers itself also.
    """

    def __init__(self):
        self.click_drag_window = None
        self.drop_list = []



    # TODO: Define register function

    # TODO: Move click drag to this class.

    # TODO: Improve dropping check to reduce walking of child widgets.

CLICK_DRAG_CONTROLLER = ClickDragController()