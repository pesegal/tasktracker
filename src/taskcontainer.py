"""
    Tasklist that handles the ordering and displaying of objects.
"""

# Todo: Implement Reordering of tasks widgets.
# Todo: Implement creation and destruction of task widgets to support moving tasks between display windows.

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button


class TaskContainer(ScrollView):
    def __init__(self, **kwargs):
        super(TaskContainer, self).__init__(**kwargs)

        # Test to add something to display information!

        items = GridLayout(cols=1, spacing=1, size_hint_y=None)
        items.bind(minimum_height=items.setter('height'))
        for i in range(30):
            btn = Button(text=str(i), size_hint_y=None, height=60)
            items.add_widget(btn)

        self.add_widget(items)


