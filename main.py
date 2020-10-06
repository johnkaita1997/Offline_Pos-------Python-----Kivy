from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from BaseAdmin.admin import AdminWindow
from BaseLogin.login import LoginWindow
from PointOfSale.pos import PosWindow

from kivy.config import Config

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '300')
from kivy.core.window import Window


class MainWindow(BoxLayout):
    admin_widget = AdminWindow()  # An instance of our Pdmin wdindow
    signin_widget = LoginWindow()  # An instance of our sign in window
    pos_widget = PosWindow() #An instance of the pos window


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.load_window()

        self.ids.scrn_admin.add_widget(self.admin_widget)
        self.ids.scrn_si.add_widget(self.signin_widget)
        self.ids.scrn_pos.add_widget(self.pos_widget)


    def load_window(self):
        # New size
        size = (1100, 630)

        # Get the actual pos and knowing the old size calcu +late the new one
        top = Window.top * Window.size[1] / size[1]
        left = Window.left * Window.size[0] / size[0]

        # Change the size
        Window.size = size

        # Fixing pos
        Window.top = top
        Window.left = left


class MainApp(App):

    def build(self):
        return MainWindow()


if __name__ == "__main__":
    sa = MainApp()
    sa.run()
