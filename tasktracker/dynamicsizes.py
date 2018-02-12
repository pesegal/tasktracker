""" Contains the calculations for all task sizes. Irregardless of screen resolution"""

from kivy.core.window import Window
from kivy.metrics import dp

def calc_height(percentage): return int(Window.height * percentage)


def calc_width(percentage): return int(Window.width * percentage)


Window.bind(width=lambda o, y: print(o.width))

# Calculated Task Height
TASK_HEIGHT = calc_height(.06)
MENU_HEIGHT = dp(30)  # calc_height(.028)

# Calculated Screen display
SCREEN_0 = dp(300)   # calc_width(.1875)
SCREEN_1 = dp(600)   # calc_width(.3333)
SCREEN_2 = dp(960)   # calc_width(.5)
SCREEN_3 = dp(1280)  # calc_width(.99)


print("Screen_0", SCREEN_0)
print("Screen_1", SCREEN_1)
print("Screen_2", SCREEN_2)
print("Screen_3", SCREEN_3)

