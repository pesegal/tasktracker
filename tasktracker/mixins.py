from math import sqrt


class Broadcast:
    def broadcast_child(self, function, **kwargs):
        """
            Broadcast a function call to all children with the broadcast mixin.
            Needs the object to inherit from kivy.uix.widget
        :param function: name of the function to call
        :param kwargs: additional arguments to send to to the function call
        """
        if hasattr(self, function) and callable(getattr(self, function)):
            func = getattr(self, function)
            func(**kwargs)

        for child in self.children:
            if hasattr(child, 'broadcast_child') and callable(getattr(child, 'broadcast_child')):
                child.broadcast_child(function, **kwargs)

    def broadcast_parent(self, function, **kwargs):
        """
            Broadcast a function call to all parents with the broadcast mixin.
            Needs the object to inherit from kivy.uix.widget
        :param function: name of the function to call
        :param kwargs: additional named arguments to send to the function call
        """
        if hasattr(self, function) and callable(getattr(self, function)):
            func = getattr(self, function)
            func(**kwargs)
        if hasattr(self.parent, 'broadcast_parent') and callable(getattr(self.parent, 'broadcast_parent')):
            self.parent.broadcast_parent(function, **kwargs)


class TapAndHold:
    # TODO: MOVE ALL OF THIS CODE INTO THE TASK OBJECT!

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._point = None  # Contains point after trigger
        self._sensitivity = 4  # Sensitivity (pixels)
        self._hold_length = 1.4  # Seconds
        self._event = None  # Outstanding event or none
        self.triggered = False  # Whether or not the event was triggered

    def _distance(self, touch):
        """ Calculate distance moved from start """
        if self._point is not None:
            dx, dy = touch.x - self._point.x, touch.y - self._point.y
            dxy = dx * dx + dy * dy
            if dxy > 0: return sqrt(dxy)
        return 0

    def _release_event(self):
        """ Free up and cancel any outstanding event """
        if self._event is not None:
            self._event.release()  # stop any outstanding events
        self._event = None

    def _long_hold(self, _dt):
        """ Comes here after a tap and hold """
        if self._event is not None:
            self.triggered = True
            self.on_tap_hold(self._point)  # Generate event
            self._release_event()

    def on_touch_move(self, touch):
        """ If there was movement, invalidate the tap+hold """
        dxy = self._distance(touch)
        if dxy > self._sensitivity:
            self._point = None  # No event triggered
            self._release_event()

    def on_touch_up(self, touch):
        """ Tap+hold is finished if it was effective """
        self._point = None
        self._release_event()

    def on_tap_hold(self, touch):
        """ To be implemented by concrete class """
        raise NotImplementedError

    def on_touch_down(self, touch):
        # Note since this will always been inherited by a widget object.
        # self should resolve to a instance of a widget.
        if self.collide_point(touch.x, touch.y):  # filter touch events
            self.triggered = False
            self._release_event()
            self._point = copy(touch)         # Touch events share an instance
            self._event = Clock.schedule_once(self._long_hold, self._hold_length)
