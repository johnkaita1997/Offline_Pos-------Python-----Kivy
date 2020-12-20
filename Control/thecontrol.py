import os

import pyrebase
from kivy import Config
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView

Config.set('graphics', 'multisamples', '0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

Builder.load_file('Control/control.kv')

class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class ControlWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.notify = Notify()
        self.firebaseconfig = {
            "apiKey": "AIzaSyDGsXv0wa7Fc4irPi3MX_uWTIfuWHeEIzU",
            "authDomain": "projectId.firebaseapp.com",
            "databaseURL": "https://cocabpos-e5199.firebaseio.com/",
            "storageBucket": "projectId.appspot.com"
        }

        self.firebase = pyrebase.initialize_app(self.firebaseconfig)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()

    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def showAlert(self, message):
        self.notify.add_widget(Label(text='[color=#FF0000][b]' + message + '[/b][/color]', markup=True))
        self.notify.open()
        Clock.schedule_once(self.killswitch, 3)

    def product_Key_Check(self):
        input = self.ids.enteredproductkey.text

        if input:

            try:
                self.users_by_name = self.db.child("Control").order_by_child("key").get().val()
                if  input in self.users_by_name.keys():
                    self.parent.parent.current = 'scrn_login'
                else:
                    self.showAlert("Product Not Verified!!!")
            except Exception as message:
                self.showAlert("Check your internet connection")

        else:
            self.showAlert("You have to enter all fields")


class ControlApp(App):
    def build(self):
        return ControlWindow()



if __name__ == '__main__':
    app = ControlApp()
    app.run()