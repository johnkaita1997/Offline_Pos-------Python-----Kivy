from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

class MainWindow(Screen):
    pass

class SecondWindow(Screen):
    pass

#This class represents the transition between windows
class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("intermediatemy.kv")

class MyApp(App):
    def build(self):
        global  root
        root = self.root
        return  kv


if __name__ == "__main__":
    MyApp().run()
