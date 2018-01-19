"""
    Author: Peter Segal
    Todo List Plus

"""
import os
import sys
from kivy.app import App
from kivy.lang import Builder
from screencontroller import ScreenClickDragWindow
from kivy.config import Config
from database.db_interface import DB
from settings.settingscontroller import APP_CONTROL
from themes import themes
from kivy.clock import Clock
import fileloader

if getattr(sys, 'frozen', False):
        # we are running in a bundle
        __location__ = sys._MEIPASS
else:
        # we are running in a normal Python environment
        __location__ = os.path.dirname(os.path.abspath(__file__))

# Load in the .kv files
layout_path = os.path.join(__location__, 'layouts')

def exception_shutdown(exctype, value, tb):
    """Actions to take if the App encounters a runtime error."""
    # Stop the current timer action
    APP_CONTROL.timer_screen.timer_reset()
    # Shut down helper threads.
    DB.thread_shutdown()
    tb.print_tb()
    print(exctype, value, tb)


class TaskApp(App):
    def build(self):
        self.title = 'TaskTracker++'
        self.minimum_width = 150
        self.minimum_height = 300
        return ScreenClickDragWindow()

    def on_stop(self):
        """Actions to take before the program closes."""
        themes.save_set_configuration()  # This saves config settings to conf
        APP_CONTROL.timer_screen.timer_reset()
        DB.thread_shutdown()


if __name__ == '__main__':
    sys.excepthook = exception_shutdown
    for file in os.listdir(layout_path):
        Builder.load_file(os.path.join(layout_path, file))
    # Load configurations
    # Disable Multi-touch for mouse
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    TaskApp().run()
