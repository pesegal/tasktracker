
class BroadcastMixin:
    def broadcast_child(self, function, **kwargs):
        """
            Broadcast a function call to all children with the broadcast mixin attaced.
        :param function: name of the function to call
        :param args: additional arguments to send to to the function call
        """
        if hasattr(self, function) and callable(getattr(self, function)):
            func = getattr(self, function)
            func(**kwargs)

        for child in self.children:
            if hasattr(child, 'broadcast_child') and callable(getattr(child, 'broadcast_child')):
                child.broadcast_child(function, **kwargs)













