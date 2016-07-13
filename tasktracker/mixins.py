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















