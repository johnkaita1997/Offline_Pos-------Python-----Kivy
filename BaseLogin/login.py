from kivy.app import App
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.clock import Clock

Config.set('graphics', 'resizable', False)
import pyrebase


Builder.load_file('BaseLogin/login.kv')

class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.3, .3)


class LoginWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.firebaseconfig = {
            "apiKey": "AIzaSyDGsXv0wa7Fc4irPi3MX_uWTIfuWHeEIzU",
            "authDomain": "projectId.firebaseapp.com",
            "databaseURL": "https://cocabpos-e5199.firebaseio.com/",
            "storageBucket": "projectId.appspot.com"
        }

        self.firebase = pyrebase.initialize_app(self.firebaseconfig)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()

        self.notify = Notify()

    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()


    def get_users(self):
        self.users = self.db.child("users").get()
        name = []
        mobile = []
        id = []
        designation = []

        for user in self.users.each():
            key = user.key()

            retrieve_name = self.db.child("users").child(key).child("name").get().val()
            name.append(retrieve_name)

            retrieve_mobile = self.db.child("users").child(key).child("mobile").get().val()
            mobile.append(retrieve_mobile)

            retrieve_id = self.db.child("users").child(key).child("id").get().val()
            id.append(retrieve_id)

            retrieve_designation = self.db.child("users").child(key).child("designation").get().val()
            designation.append(retrieve_designation)

        return (name)


    def get_products(self):

        self.users = self.db.child("stocks").get()

        product_name = []
        product_code = []
        productinstock = []
        productsold = []
        lastpurchased = []

        for user in self.users.each():
            key = user.key()

            retrieve_name = self.db.child("users").child(key).child("product_name").get().val()
            product_name.append(retrieve_name)

            retrieve_mobile = self.db.child("users").child(key).child("product_code").get().val()
            product_code.append(retrieve_mobile)

            retrieve_id = self.db.child("users").child(key).child("productinstock").get().val()
            productinstock.append(retrieve_id)

            retrieve_designation = self.db.child("users").child(key).child("productsold").get().val()
            productsold.append(retrieve_designation)

            productsold = self.db.child("users").child(key).child("lastpurchased").get().val()
            productsold.append(lastpurchased)


        return (product_name)



    def login_user(self):
        theemail = self.ids.email.text
        thepassword = self.ids.password.text

        if theemail ==  '' or thepassword == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)

        else:
            #Get the credential using password
            operation = self.db.child("users").child(thepassword).child('designation').get().val()

            if operation == '' or operation == None:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Wrong Credentials[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                print(operation)
                if operation == 'Administrator':
                    self.parent.parent.current = 'scrn_admin'
                elif operation == 'Operator':
                    self.parent.parent.current = 'scrn_pos'
                else:
                    self.notify.add_widget(Label(text='[color=#FF0000][b]An error occured[/b][/color]', markup=True))
                    self.notify.open()
                    Clock.schedule_once(self.killswitch, 1)


class LogInApp(App):

    def build(self):
        return LoginWindow()


if __name__ == "__main__":
    active_App = LogInApp()
    active_App.run()
