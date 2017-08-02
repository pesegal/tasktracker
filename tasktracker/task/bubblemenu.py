from kivy.uix.button import Button
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.properties import ListProperty, StringProperty

from tasktracker.task.taskpopups import TaskEditScreen
from tasktracker.themes.themes import Themeable
from tasktracker.themes import themes
from tasktracker.settings.settingscontroller import APP_CONTROL


class TaskQuickMenu(Bubble, Themeable):
    shadow_texture = StringProperty(themes.SHADOW_TEXTURE)
    bg_texture = StringProperty(themes.ALL_BEV_CORNERS)
    bg_color = ListProperty()

    def __init__(self, task, **kwargs):
        super().__init__(**kwargs)
        self.task = task
        self.size = (self.task.width - 30, 10)
        self.bg_color = self.theme.status
        self.content.padding = 2
        self.content.spacing = 2

    def theme_update(self):
        self.bg_color = self.theme.status

    def _close_menu(self):
        self.parent.remove_widget(self)

    def _open_edit_screen(self):
        TaskEditScreen(self.task).open()
        self._close_menu()

    def _work_timer(self):
        APP_CONTROL.timer_task_manager.load_task(self.task)
        APP_CONTROL.menu_bar.switch_screens('timer')
        self._close_menu()

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            self._close_menu()
        elif 'button' in touch.profile and touch.button != 'left':
            self._close_menu()
        else:
            return super().on_touch_down(touch)


class QuickMenuButton(Button, Themeable):
    button_texture = StringProperty(themes.NO_BEV_CORNERS)
    button_color = ListProperty()
    text_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button_color = self.theme.tasks
        self.text_color = self.theme.text
        self.text_color[3] = .8

    def theme_update(self):
        self.button_color = self.theme.tasks
        self.text_color = self.theme.text
        self.text_color[3] = .8

    def on_press(self):
        print(self, "TOUCHED")

    def on_state(self, widget, value):
        if self.state == 'down':
            self.button_color = self.theme.selected
        else:
            self.button_color = self.theme.tasks