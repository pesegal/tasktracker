""" Contains the calculations for all task sizes. Irregardless of screen resolution"""

from kivy.core.window import Window


def calc_height(percentage): return int(Window.height * percentage)


def calc_width(percentage): return int(Window.width * percentage)


# Calculated Task Height
TASK_HEIGHT = calc_height(.06)

# Calculated Screen display
SCREEN_0 = calc_width(.1875)
SCREEN_1 = calc_width(.3333)
SCREEN_2 = calc_width(.5)
SCREEN_3 = calc_width(.70)
