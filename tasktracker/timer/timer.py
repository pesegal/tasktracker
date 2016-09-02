""" The Timer module contains all of the controller logic for the timer In the system.
"""

from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class TimerScreen(Screen):
    current_time = NumericProperty(0)


    def on_start(self):
        Clock.schedule_interval(self.update, 0.016)

    def update(self, nap):
        self.current_time += nap
        minutes, seconds = divmod(self.current_time, 60)
        self.ids.timer.text = ('%02d:%02d' % (int(minutes), int(seconds)))



    def update_time(self, nap):
        pass