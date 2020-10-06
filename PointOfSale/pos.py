from random import  randint
import pyrebase
from datetime import date
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.factory import Factory

Config.set('graphics', 'resizable', False)
from kivy.uix.boxlayout import BoxLayout

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '300')
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, DictProperty
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
import tempfile

Builder.load_file('PointOfSale/pos.kv')


class LongpressButton(Factory.Button):
    __events__ = ('on_long_press',)

    long_press_time = Factory.NumericProperty(1)

    def on_state(self, instance, value):
        if value == 'down':
            lpt = self.long_press_time
            self._clockev = Clock.schedule_once(self._do_long_press, lpt)
        else:
            self._clockev.cancel()

    def _do_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        pass


class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.3, .3)


class OpenDialog(Popup):
    _age = NumericProperty()
    error = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._age = 0

    def on_error(self, inst, text):
        if text:
            self.lb_error.size_hint_y = 1
            self.size = (400, 150)
        else:
            self.lb_error.size_hint_y = None
            self.lb_error.height = 0
            self.size = (400, 120)

    def _enter(self):
        if not self.text:
            self.error = "Error: enter age"
        else:
            self._age = int(self.text)
            self.dismiss()

    def _cancel(self):
        self.dismiss()


class PosWindow(BoxLayout):
    thebox = ObjectProperty(None)
    dynamic_ids = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.load_window()
        self.receipt_Preview = self.ids.receipt_Preview

        self.filename = tempfile.mktemp(".txt")

        self.complete_total = 0.00
        self.discount = 0.00
        self.productList = {}
        self.activ_product = []
        self.final_Amount = 0.00

        self.cred = credentials.Certificate('privatekey.json')

        self.ref = db.reference()

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

        # Load the spinner values
        prods = self.db.child("categorylist").get().val()

        # Load the values from the database
        self.thespinner = self.ids.thespinner
        self.thespinner.values = prods.values()

        # Add the spinner onclickListener
        self.thespinner.bind(text=self.on_spinner_select)

        # call back for the selection in spinner object
        self.theids = {}

        self.thesumsList = []

        self.listofKeys = []

        self.listofKeys = self.productList.keys()

        # Load the values from the database
        self.payment_spinner = self.ids.payment_spinner
        self.payment_spinner.values = ['Cash', 'M-Pesa', 'Card']

        # Add the spinner onclickListener
        self.payment_spinner.bind(text=self.on_purchase_spinner_select)

    def on_purchase_spinner_select(self, spinner, text):
        self.receivedSpinnerText = text
        #Get the other variables and add them to the database
        today = date.today()
        total_amount = self.final_Amount

        #Retrieve the productList
        numberofitems = len(self.productList)
        paymenttype = text


        # Item already exists, try and get the name of the text
        thetext = self.ids.thetotal.text

        # Split on colon
        thetext_splitted = thetext.split(":")

        # Get last value (strip() removes spaces)
        last_value = thetext_splitted[-1].strip()

        datte = {}
        datte["date"] = str(today)
        datte["amount"] = last_value
        datte["number"] = numberofitems
        datte["payment"] = paymenttype

        self.db.child("sales").child(randint(1, 1000000)).set(datte)

    def on_spinner_select(self, spinner, text):

        self.spinnertext = text

        # Add Widgets to button
        target = self.ids.thebox
        target.clear_widgets()

        ref = db.reference('products')
        snapshot = ref.order_by_child("category").start_at(self.spinnertext).end_at(
            self.spinnertext + "\uf8ff").get() or ref.order_by_child("code").start_at(self.spinnertext).end_at(
            self.spinnertext + "\uf8ff").get()

        for value in snapshot.values():
            name = value['name']
            code = value['code']
            buyingprice = value['buyingprice']
            sellingprice = value['sellingprice']
            category = value['category']

            name = Button(text=str(name) + " " + str(code) + " " + str(sellingprice), size_hint_x=1, width=40,
                          size_hint_y=None, height=30,
                          on_release=lambda button: self.show_result(button.text))

            target.add_widget(name)

    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def searchforproduct(self):

        self.searchQuery = self.ids.qty_inp.text

        # Add Widgets to button
        target = self.ids.thebox
        target.clear_widgets()

        if self.searchQuery == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)

        else:

            ref = db.reference('products')
            snapshot = ref.order_by_child("name").start_at(self.searchQuery).end_at(
                self.searchQuery + "\uf8ff").get() or ref.order_by_child("code").start_at(self.searchQuery).end_at(
                self.searchQuery + "\uf8ff").get()

            for value in snapshot.values():
                name = value['name']
                code = value['code']
                buyingprice = value['buyingprice']
                sellingprice = value['sellingprice']
                category = value['category']

                name = Button(text=str(name) + " " + str(code) + " " + str(sellingprice), size_hint_x=1, width=40,
                              on_release=lambda button: self.show_result(button.text))

                target.add_widget(name)

    def show_result(self, x):
        resultString = x
        # split the text
        words = resultString.split()

        self.callit()

        current_Item_Name = words[0]
        current_Item_Code = words[1]
        current_Item_Price = words[2]

        self.ids.cur_product.text = current_Item_Name  # Set the name
        self.ids.cur_price.text = "KES: " + current_Item_Price

        target = self.ids.receipt_Preview
        # target.clear_widgets()

        # Check if buttton i s already in the dict meaining it has been added
        if current_Item_Name in self.productList:

            # Item already exists, try and get the name of the text
            thetext = self.dynamic_ids[current_Item_Name].text

            # Split on colon
            thetext_splitted = thetext.split(":")

            # Get last value (strip() removes spaces)
            last_value = thetext_splitted[-1].strip()

            thenumber = 1

            # Firest of all get the text from the box, if it is null user has not entered the numbher.
            getText = self.ids.number.text
            if (getText == ''):
                thenumber = 1

            else:
                thenumber = int(self.ids.number.text)

            words.insert(3, thenumber)

            new_last_value = str(int(last_value) + thenumber)

            # Create the new list, updated with the new value
            thetext_splitted[-1] = new_last_value

            # Recreate "thetext"
            new_thetext = ":".join(thetext_splitted)

            self.dynamic_ids[current_Item_Name].text = new_thetext

            # Activate the active product
            self.activ_product = current_Item_Name

            # Update Complete Total
            self.complete_total = current_Item_Price
            self.ids.thetotal.text = self.complete_total

            self.ids.number.text = ''

            self.productList[current_Item_Name][3] = new_last_value

            for item in self.listofKeys:
                thequantity = self.productList[item][3]
                thecash = self.productList[item][2]
                multiplied = float(thequantity) * float(thecash)
                self.thesumsList.append(multiplied)

            self.ids.thetotal.text = "Total Payable: " + str(
                sum(float(entry[2]) * float(entry[3]) for entry in self.productList.values()))

        else:

            crud_submit = LongpressButton(long_press_time=2, id=current_Item_Name,
                                          text=current_Item_Name + "    Price:" + current_Item_Price + "     Qty: 1",
                                          size_hint_x=1, size_hint_y=None, height=30,
                                          on_long_press=lambda button: self.longPressed(current_Item_Name, button),
                                          on_press=lambda button: self.make_active_toChangeStuff(button.text))

            target.add_widget(crud_submit)

            # Activate the active product
            self.activ_product = current_Item_Name

            # Update Complete Total
            self.complete_total = float(self.complete_total) + float(current_Item_Price)
            self.ids.thetotal.text = str(self.complete_total)

            # Add the product to product List
            self.productList[current_Item_Name] = words

            self.theids[current_Item_Name] = current_Item_Name
            self.dynamic_ids[current_Item_Name] = crud_submit
            self.productList[current_Item_Name].insert(3, 1)

            for item in self.listofKeys:
                thequantity = self.productList[item][3]
                thecash = self.productList[item][2]
                multiplied = float(thequantity) * float(thecash)
                self.thesumsList.append(multiplied)

            self.ids.thetotal.text = "Total Payable: " + str(
                sum(float(entry[2]) * float(entry[3]) for entry in self.productList.values()))

    def change_quantity(self):
        # Get the text given
        added_qty = self.ids.number.text
        if (added_qty == ''):
            self.notify.add_widget(Label(text='[color=#FF0000][b] Enter valid Input[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            # use active product to get the price and the quantity of the current prodouct
            # Get the current price
            # Go into words and get the this active item
            theresut = self.productList.get(self.activ_product)

            # #Now we need to change the value of the total
            # newTotal = self.complete_total * float(theresut[2])
            # self.complete_total = newTotal

            theresut[3] = added_qty

            # Item already exists, try and get the name of the text
            thetext = self.dynamic_ids[self.activ_product].text
            # Split on colon
            thetext_splitted = thetext.split(":")
            # Get last value (strip() removes spaces)
            last_value = thetext_splitted[-1].strip()
            # Firest of all get the text from the box, if it is null user has not entered the numbher.
            new_last_value = added_qty
            # Create the new list, updated with the new value
            thetext_splitted[-1] = new_last_value
            # Recreate "thetext"
            new_thetext = ":".join(thetext_splitted)
            self.dynamic_ids[self.activ_product].text = new_thetext

            # Activate the active product
            self.activ_product = self.activ_product

            # Update Complete Total
            self.ids.thetotal.text = str(self.complete_total)
            self.ids.number.text = ''

            self.productList[self.activ_product][3] = new_last_value

            for item in self.listofKeys:
                thequantity = self.productList[item][3]
                thecash = self.productList[item][2]
                multiplied = float(thequantity) * float(thecash)
                self.thesumsList.append(multiplied)

            self.ids.thetotal.text = "Total Payable: " + str(
                sum(float(entry[2]) * float(entry[3]) for entry in self.productList.values()))

    def change_discount(self):

        added_discount = self.ids.discount.text
        if (added_discount == '' or added_discount == None):
            self.notify.add_widget(Label(text='[color=#FF0000][b] Enter valid Input[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:

            for item in self.listofKeys:
                thequantity = self.productList[item][3]
                thecash = self.productList[item][2]
                multiplied = float(thequantity) * float(thecash)
                self.thesumsList.append(multiplied)

            self.ids.thetotal.text = "Total Payable: " + str( sum(float(entry[2]) * float(entry[3]) for entry in self.productList.values()) - float(added_discount))
            self.final_Amount = sum( float(entry[2]) * float(entry[3]) for entry in self.productList.values()) - float(added_discount)

    def longPressed(self, itemId, button):
        # Now get the active product and get the total and remove the total
        active = self.activ_product

        # Get the total amount of active product
        retrieve = self.productList.get(active)
        amount = retrieve[2]
        self.complete_total = float(self.complete_total) - float(amount)

        # Remove the widget
        target = self.ids.receipt_Preview

        button.size_hint_y = None
        button.opacity = 0
        button.height = 0

        # Remove item from the dictionary as well
        self.productList.pop(active, None)

        for item in self.listofKeys:
            thequantity = self.productList[item][3]
            thecash = self.productList[item][2]
            multiplied = float(thequantity) * float(thecash)
            self.thesumsList.append(multiplied)

        self.ids.cur_price.text = "0.0"
        self.ids.cur_product.text = "Default Product"

        self.ids.thetotal.text = "Total Payable: " + str(
            sum(float(entry[2]) * float(entry[3]) for entry in self.productList.values()))

    def make_active_toChangeStuff(self, text):
        thenewList = text.split()
        thename = thenewList[0]

        # Loop through active products and make the selected product active
        resultantList = self.productList.get(thename)

        self.ids.cur_product.text = resultantList[0]  # Set the name
        self.ids.cur_price.text = "KES: " + resultantList[0]
        self.activ_product = thename

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

    def callit(self):
        # obj = OpenDialog()
        # obj.open()
        pass

    def on_age(self, *args):
        self.str_age = "Age: {}".format(self.age)
        print(self.age)

    def clearWidgets(self):
        self.ids.receipt_Preview.clear_widgets()
        self.productList.clear()
        self.thesumsList.clear()
        self.complete_total = 0.00
        self.ids.cur_price.text = "0.0"
        self.ids.cur_product.text = "Default Product"
        self.ids.thetotal.text = "Total: 0.0"
        self.final_Amount = 0.0

    def logout(self):
        self.parent.parent.current = 'scrn_login'

    def print_output(self):
        if any(self.productList) == False:
            self.notify.add_widget(Label(text='[color=#FF0000][b]Add Items First[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            # Item already exists, try and get the name of the text
            thetext = self.ids.thetotal.text
            # Split on colon
            thetext_splitted = thetext.split(":")
            # Get last value (strip() removes spaces)
            last_value = thetext_splitted[-1].strip()

            open(self.filename, "w").write("Items :" + str(self.productList.keys()) + "Total Due: " + last_value)
            os.startfile(self.filename, "print")


class PosApp(App):

    def build(self):
        return PosWindow()


if __name__ == "__main__":
    sa = PosApp()
    sa.run()
