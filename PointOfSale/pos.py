import io
from datetime import date
import datetime
from kivy.uix.image import Image, CoreImage
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.factory import Factory
from testmysql import mycursor, db
import datetime
import io
from datetime import date
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.image import Image, CoreImage
from kivy.uix.modalview import ModalView
from testmysql import mycursor, db
Config.set('graphics', 'resizable', False)
from kivy.uix.boxlayout import BoxLayout
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '300')
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.properties import DictProperty
import os
import tempfile
import overall
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from random import randint
from BaseAdmin.admin import AdminWindow

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

class PosWindow(BoxLayout):
    thebox = ObjectProperty(None)
    dynamic_ids = DictProperty()
    headerlabel = StringProperty()
    reallocation = StringProperty()
    user = StringProperty()
    prods = ListProperty()
    thespinner = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.haschoosentopay = ''

        self.load_window()
        self.receipt_Preview = self.ids.receipt_Preview

        self.headerlabel = "fuck you"

        self.filename = tempfile.mktemp(".txt")
        self.customerpayed = ''
        self.customerbalance = ''
        self.complete_total = 0.00
        self.discount = 0.00
        self.productList = {}
        self.final_Amount = 0.00
        self.amountinput = self.ids.amountinput.text  # Load those values from the database
        self.mpesacode = self.ids.mpesacode.text
        self.finalvariables = []
        self.notify = Notify()
        self. mylocation = self.reallocation
        self.totaltoBePaid = 0.0


        mycursor.execute("SELECT * FROM categorylist")
        data = mycursor.fetchall()  # get the data in data variabl
        self.prods = [value[0] for value in data]

        self.headerlabel = overall.heading + "                             |                                " +  self.user +  "                             "

        # Load the values from the database
        self.thespinner = self.ids.thespinner
        self.thespinner.values = self.prods

        # call back for the selection in spinner object
        self.theids = {}

        self.thesumsList = []

        self.listofKeys = []

        self.listofKeys = self.productList.keys()

        # Load the values from the database
        self.payment_spinner = self.ids.payment_spinner
        self.payment_spinner.values = ['Cash', 'M-Pesa', 'Card']

        self.payment_Mode = ''

        self.paymenthold = self.ids.paymenthold
        self.paymenthold.values = ['Hold', 'Resume', 'Clear']

        self.loadinititalproducts()

    def loadinititalproducts(self):

        # Add Widgets to button
        target = self.ids.thebox
        target.clear_widgets()

        mycursor.execute("SELECT * FROM products WHERE  location=%s",(self.reallocation,))

        row = mycursor.fetchall()
        if row == None or row == []:

            mycursor.execute("SELECT * FROM products WHERE  location=%s",  (self.reallocation,))

            urow = mycursor.fetchall()
            if urow == None or urow == []:
                self.showAlert("No results found")
                pass
            else:
                for value in row:
                    name = value[3]
                    code = value[2]
                    sellingprice = value[4]
                    name = Button(text=str(name) + " " + str(code) + " " + str(sellingprice),
                                  size_hint_x=1, width=40, size_hint_y=None, height=30,
                                  on_release=lambda button: self.show_result(button.text))

                    if value[9]:
                        image = value[9]
                        data = io.BytesIO(image)
                        img = CoreImage(data, ext="png").texture
                        widget = Image(source='a.jpg')
                        widget.texture = img
                        widget.size_hint_y = None
                        widget.size_hint_x = 1
                        target.add_widget(widget)

                    target.add_widget(name)
                    name = Label(text='\n\n\n\n',
                                 size_hint_x=1, width=40, size_hint_y=None, height=30)
                    target.add_widget(name)

        else:
            for value in row:
                name = value[3]
                code = value[2]
                sellingprice = value[4]
                name = Button(text=str(name) + " " + str(code) + " " + str(sellingprice),
                              size_hint_x=1, width=40, size_hint_y=None, height=30,
                              on_release=lambda button: self.show_result(button.text))

                if value[9]:
                    image = value[9]
                    data = io.BytesIO(image)
                    img = CoreImage(data, ext="png").texture
                    widget = Image(source='a.jpg')
                    widget.texture = img
                    widget.size_hint_y = None
                    widget.size_hint_x = 1
                    target.add_widget(widget)

                target.add_widget(name)
                name = Label(text='\n\n\n\n',
                             size_hint_x=1, width=40, size_hint_y=None, height=30)
                target.add_widget(name)

    def checkifadmin(self):
        self.activ_product = []

        # Load those values from the database
        mycursor.execute("SELECT username FROM Active WHERE location=%s", (self.reallocation,))
        data = mycursor.fetchone()
        overall.username = str(data[0])

        print(self.user)

        # Load those values from the database
        if(self.user == 'Admin'):
            AdminWindow.loadEverything(self.parent.parent.parent.admin_widget)
            self.parent.parent.current = 'scrn_admin'


    def selectedCustomer(self, text):
        identifier = str(randint(1, 1000)) + " " + str(datetime.datetime.now())
        datte = {}
        datte['name'] = identifier

        if text == 'Hold':
            if not self.productList:
                self.notify.add_widget(Label(text='[color=#FF0000][b]' + "No items in cart to add" + '[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 5)
            else:
                mycursor.execute("""INSERT INTO holdkeys (name)  VALUES (%(name)s)""", datte)
                db.commit()
                for key, values in self.productList.items():
                    datte = {}
                    name = values[0]
                    code = values[1]
                    price = values[2]
                    quantity = values[3]

                    datte['name'] = name
                    datte['code'] = code
                    datte['price'] = price
                    datte['quantity'] = quantity
                    datte['identifier'] = identifier

                    #Add each of these values to the database
                    mycursor.execute(
                        """INSERT INTO hold (name, code, price, quantity, identifier)  VALUES (%(name)s, %(code)s,  %(price)s,  %(quantity)s, %(identifier)s)""",
                        datte)
                    db.commit()

                self.clearWidgets()
                # Add Widgets to button
                target = self.ids.thebox
                target.clear_widgets()

                #Delete from the database where the key is the seam as the one above
                self.showAlert("Operation was successful")

        elif text == 'Resume':
            # Add Widgets to button
            target = self.ids.thebox
            target.clear_widgets()
            self.clearWidgets()

            mycursor.execute("SELECT * FROM holdkeys")
            data = mycursor.fetchall()  # get the data in data variabl
            if(data):
                for value in data:
                    name = value[0]
                    name = Button(text=str(name),
                                  size_hint_x=1, width=40,
                                  size_hint_y=None, height=30,
                                  on_release=lambda button: self.resume_button_get_text(button.text))
                    target.add_widget(name)
            else:
                self.showAlert("No items on hold")

        elif text == 'Clear':
            try:
                mycursor.execute("DELETE FROM holdkeys")
                mycursor.execute("DELETE FROM hold")
                db.commit()
            except:
                self.showAlert("An internal error occured")
            else:
                self.showAlert("Operation was successful")

    def  resume_button_get_text(self, text):
        identifier = text
        mycursor.execute("SELECT * FROM hold WHERE identifier=%s", (identifier,))
        data = mycursor.fetchall()
        target = self.ids.receipt_Preview
        target.clear_widgets()
        for user in data:
            name = user[0]
            code = user[1]
            price = user[2]
            quantity = user[3]
            crud_submit = LongpressButton(long_press_time=2, id=name,
                                          text=name + "    Price:" + price + "     Qty: " + quantity,
                                          size_hint_x=1, size_hint_y=None, height=30,
                                          on_long_press=lambda button: self.longPressed(name, button),
                                          on_press=lambda button: self.make_active_toChangeStuff(button.text))

            target.add_widget(crud_submit)

            # Add the product to product List
            self.dynamic_ids[name] = crud_submit
            self.productList[name] = [name, code, price, quantity]

            thequantity = float(quantity)
            thecash = float(price)
            multiplied = float(thequantity) * float(thecash)
            self.thesumsList.append(multiplied)

        target = self.ids.thebox
        target.clear_widgets()
        self.ids.thetotal.text = "Total Payable: " + str(sum(float(user[2]) * float(user[3]) for user in data))

        try:
            mycursor.execute("DELETE FROM holdkeys WHERE name=%s", (identifier,))
            mycursor.execute("DELETE FROM hold WHERE identifier=%s", (identifier,))
            db.commit()
        except:
            self.showAlert("An internal error occured")
        else:
            self.showAlert("Operation was successful")


    def on_purchase_spinner_select(self, text):

        self.receivedSpinnerText = text
        #Get the other variables and add them to the database
        today = date.today()
        total_amount = self.final_Amount

        self.amountinput = self.ids.amountinput.text
        self.mpesacode = self.ids.mpesacode.text

        #Retrieve the productList
        numberofitems = len(self.productList)
        paymenttype = text

        # Item already exists, try and get the name of the text
        thetext = self.ids.thetotal.text
        # Split on colon
        thetext_splitted = thetext.split(":")
        # Get last value (strip() removes spaces)
        last_value = thetext_splitted[-1].strip()
        self.payment_Mode = self.receivedSpinnerText
        today = datetime.datetime.today()
        confirmationcode = "None"


        if paymenttype == 'M-Pesa' or paymenttype == 'Cash':
            if self.amountinput == '':
                self.showAlert("Enter Client Cash")
            else:
                if self.mpesacode == '':
                    self.showAlert('Enter Confirmation Code')
                else:

                    toPrintA = '{:>15} {:>10} {:>10}'.format("Item", "Qty", "Amount")
                    toPrintB = []

                    for key, values in self.productList.items():
                        toPrintB.append('{:>15} {:>10} {:>10}'.format(key, values[3], values[2]))

                    assin = '\n'.join(map(str, toPrintB))

                    output = toPrintA + "\n" + assin

                    print(str(output))

                    confirmationcode = self.mpesacode
                    datte = {}
                    datte["date"] = str(today.date())
                    datte["month"] = str(today.month)
                    datte["year"] = str(today.year)
                    datte["day"] = str(today.day)
                    datte["amount"] = str(last_value)
                    datte["number"] = str(numberofitems)
                    datte["payment"] = str(paymenttype)
                    datte["served"] = str(self.user)
                    datte["location"] = str(self.reallocation)
                    datte["customerpay"] = str(self.amountinput)
                    datte["balance"] = str(float(self.amountinput) - float(last_value))
                    datte["confirmationcode"] = confirmationcode
                    datte["products"] = str(output)

                    self.totaltoBePaid = last_value

                    if float(last_value) > 0:
                      self.ids.thebalance.text = str(float(self.amountinput) - float(last_value))

                    self.customerbalance = str(float(self.amountinput) - float(last_value))
                    self.customerpayed = str(self.amountinput)

                    self.finalvariables.append(str(float(self.amountinput) - float(last_value)))
                    self.finalvariables.append(self.customerpayed)

                    if any(self.productList) == False:
                        self.notify.add_widget(Label(text='[color=#FF0000][b]Add Items First[/b][/color]', markup=True))
                        self.notify.open()
                        Clock.schedule_once(self.killswitch, 5)
                    else:
                        try:
                            mycursor.execute(
                                """INSERT INTO sales (date, month, year, day, amount, number, payment, served, location, customerpay, balance, confirmationcode, products)VALUES (%(date)s, %(month)s, %(year)s,  %(day)s, %(amount)s, %(number)s, %(payment)s, %(served)s, %(location)s, %(customerpay)s, %(balance)s, %(confirmationcode)s, %(products)s)""",
                                datte)
                            db.commit()
                        except:
                            self.showAlert("An error occured\nC.Code must be unique")
                        else:
                            self.showAlert("Operation was successful")

        else:
            self.showAlert("Currently Unavailable")


    def on_spinner_select(self, text):
        self.spinnertext = text

        # Add Widgets to button
        target = self.ids.thebox
        target.clear_widgets()

        if(self.spinnertext != 'Select'):

            mycursor.execute("SELECT * FROM products WHERE category=%s and location=%s",(self.spinnertext, self.reallocation))
            row = mycursor.fetchall()
            if row == None or row == []:
                mycursor.execute("SELECT * FROM products WHERE code=%s and location=%s",  (self.spinnertext, self.reallocation))

                urow = mycursor.fetchall()
                if urow == None or urow == []:
                    self.showAlert("No results found")
                    pass
                else:
                    for value in row:
                        name = value[3]
                        code = value[2]
                        sellingprice = value[4]
                        name = Button(text=str(name) + " " + str(code) + " " + str(sellingprice),
                                      size_hint_x=1, width=40, size_hint_y=None, height=30,
                                      on_release=lambda button: self.show_result(button.text))

                        if value[9]:
                            image = value[9]
                            data = io.BytesIO(image)
                            img = CoreImage(data, ext="png").texture
                            widget = Image(source='a.jpg')
                            widget.texture = img
                            widget.size_hint_y = None
                            widget.size_hint_x = 1
                            target.add_widget(widget)

                        target.add_widget(name)
                        name = Label(text='\n\n\n\n',
                                     size_hint_x=1, width=40, size_hint_y=None, height=30)
                        target.add_widget(name)

            else:
                for value in row:
                    name = value[3]
                    code = value[2]
                    sellingprice = value[4]
                    name = Button(text=str(name) + " " + str(code) + " " + str(sellingprice),
                                  size_hint_x=1, width=40, size_hint_y=None, height=30,
                                  on_release=lambda button: self.show_result(button.text))

                    if value[9]:
                        image = value[9]
                        data = io.BytesIO(image)
                        img = CoreImage(data, ext="png").texture
                        widget = Image(source='a.jpg')
                        widget.texture = img
                        widget.size_hint_y = None
                        widget.size_hint_x = 1
                        target.add_widget(widget)

                    target.add_widget(name)
                    name = Label(text='\n\n\n\n',
                                 size_hint_x=1, width=40, size_hint_y=None, height=30)
                    target.add_widget(name)

    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def showAlert(self, message):
        self.notify.add_widget(Label(text='[color=#FF0000][b]' + message + '[/b][/color]', markup=True))
        self.notify.open()
        Clock.schedule_once(self.killswitch, 5)

    def searchforproduct(self):

        self.searchQuery = self.ids.qty_inp.text

        # Add Widgets to button
        target = self.ids.thebox
        target.clear_widgets()

        if self.searchQuery == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)

        else:
            mycursor.execute("SELECT * FROM products WHERE location =%s and code LIKE %s",(self.reallocation, "%" + self.searchQuery + "%",))
            row = mycursor.fetchall()
            if row == None or row == []:
                mycursor.execute("SELECT * FROM products WHERE location =%s and name LIKE %s", (self.reallocation, "%" + self.searchQuery + "%",))
                urow = mycursor.fetchall()
                if urow == None or urow == []:
                    self.showAlert("No results found")
                else:
                    for value in urow:
                        name = value[3]
                        code = value[2]
                        sellingprice = value[4]
                        name = Button(text=str(name) + " " + str(code) + " " + str(sellingprice),
                                      size_hint_x=1, width=40, size_hint_y=None, height=30,
                                      on_release=lambda button: self.show_result(button.text))

                        if value[9]:
                            image = value[9]
                            data = io.BytesIO(image)
                            img = CoreImage(data, ext="png").texture
                            widget = Image(source='a.jpg')
                            widget.texture = img
                            widget.size_hint_y = None
                            widget.size_hint_x = 1
                            target.add_widget(widget)

                        target.add_widget(name)
                        name = Label(text='\n\n\n\n',
                                     size_hint_x=1, width=40, size_hint_y=None, height=30)
                        target.add_widget(name)
            else:
                for value in row:
                    name = value[3]
                    code = value[2]
                    sellingprice = value[4]
                    name = Button(text=str(name) + " " + str(code) + " " + str(sellingprice),
                                  size_hint_x=1, width=40, size_hint_y=None, height=30,
                                  on_release=lambda button: self.show_result(button.text))

                    if value[9]:
                        image = value[9]
                        data = io.BytesIO(image)
                        img = CoreImage(data, ext="png").texture
                        widget = Image(source='a.jpg')
                        widget.texture = img
                        widget.size_hint_y = None
                        widget.size_hint_x = 1
                        target.add_widget(widget)

                    target.add_widget(name)
                    name = Label(text='\n\n\n\n',
                                 size_hint_x=1, width=40, size_hint_y=None, height=30)
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

        #Validate this product firs
        mycursor.execute("SELECT * FROM products WHERE code=%s and location=%s", (current_Item_Code, self.reallocation))
        data = mycursor.fetchone()

        if(data):
            #Loop through the values
            present = data[5]
            stock = data[6]
            if(present  == 'Available'):
                if(stock == '' or stock == None or stock == '0'):
                    self.showAlert("Item out of stock")
                else:

                    # Check if buttton i s already in the dict meaining it has been added
                    if current_Item_Name in self.productList:


                        #BEGINNING OF OPERATION ON STRING

                        #Dynamic ids is simply a storage list that keeps list of the IDS
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



                        #END OF OPERATION ON STRING I CAN NOW VALIDATE THE STRING

                        # Loop through the values
                        stock = data[6]
                        if float(new_last_value) > float(stock):
                            self.showAlert("Unable to add..Only " + stock + " kg left\n")
                        else:

                            #UPdating visible text with the new text including new number which is new_thetext
                            self.dynamic_ids[current_Item_Name].text = new_thetext

                            # Activate the active product
                            self.activ_product = current_Item_Name

                            # Update Complete Total
                            self.complete_total = current_Item_Price
                            self.ids.thetotal.text = self.complete_total

                            self.ids.number.text = ''



                            #Adding to the product list array...am  now adding the new number
                            self.productList[current_Item_Name][3] = new_last_value

                            for item in self.listofKeys:
                                thequantity = self.productList[item][3]
                                thecash = self.productList[item][2]
                                multiplied = float(thequantity) * float(thecash)
                                self.thesumsList.append(multiplied)

                            self.ids.thetotal.text = "Total Payable: " + str(
                                sum(float(entry[2]) * float(entry[3]) for entry in self.productList.values()))

                    else:

                        # Loop through the values
                        stock = data[6]
                        if float(1) > float(stock):
                            self.showAlert("Unable to add..Only " + stock + " kg left")
                        else:

                            crud_submit = LongpressButton(long_press_time=2, id=current_Item_Name,
                                                          text=current_Item_Name + "    Price:" + current_Item_Price + "     Qty: 1",
                                                          size_hint_x=1, size_hint_y=None, height=30,
                                                          on_long_press=lambda button: self.longPressed(current_Item_Name,
                                                                                                        button),
                                                          on_press=lambda button: self.make_active_toChangeStuff(
                                                              button.text))

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
                            #Adding quantity to be 1 in position 3 or Array
                            self.productList[current_Item_Name].insert(3, 1)

                            for item in self.listofKeys:
                                thequantity = self.productList[item][3]
                                thecash = self.productList[item][2]
                                multiplied = float(thequantity) * float(thecash)
                                self.thesumsList.append(multiplied)

                            self.ids.thetotal.text = "Total Payable: " + str(
                                sum(float(entry[2]) * float(entry[3]) for entry in self.productList.values()))


            elif(present == 'Unavailable'):
                self.showAlert("Item not available for sale")
            else:
                self.showAlert("Not available for sale")

        else:
            self.showAlert("Errror!! \nCould not find item")


    def change_quantity(self):
        # Get the text given
        added_qty = self.ids.number.text
        #Get the item in 1st position from name, ie code
        if(added_qty):
            code = self.productList.get(self.activ_product)[1]
            # Validate this product firs
            mycursor.execute("SELECT * FROM products WHERE code=%s and location =%s", (code, self.reallocation))
            data = mycursor.fetchone()

            if (data):
                # Loop through the values
                stock = data[6]
                if float(added_qty) > float(stock):
                    self.showAlert("Only " + stock + " items left")
                else:

                    if (added_qty == ''):
                        self.notify.add_widget(Label(text='[color=#FF0000][b] Enter valid Input[/b][/color]', markup=True))
                        self.notify.open()
                        Clock.schedule_once(self.killswitch, 5)
                    else:

                        # First of all load all the data bevore picking the quantity using code
                        # Get the current price
                        # Go into words and get the this active item
                        theresut = self.productList.get(self.activ_product)

                        #It is a good thng I was refreshing the values
                        #Now I only need to first validate then find the quotient
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
                        finalNewQuantiy = added_qty
                        # Create the new list, updated with the new value
                        thetext_splitted[-1] = finalNewQuantiy
                        # Recreate "thetext"
                        new_thetext = ":".join(thetext_splitted)
                        self.dynamic_ids[self.activ_product].text = new_thetext

                        # Activate the active product
                        self.activ_product = self.activ_product

                        # Update Complete Total
                        self.ids.thetotal.text = str(self.complete_total)
                        self.ids.number.text = ''

                        self.productList[self.activ_product][3] = finalNewQuantiy

                        for item in self.listofKeys:
                            thequantity = self.productList[item][3]
                            thecash = self.productList[item][2]
                            multiplied = float(thequantity) * float(thecash)
                            self.thesumsList.append(multiplied)

                        self.ids.thetotal.text = "Total Payable: " + str(
                            sum(float(entry[2]) * float(entry[3]) for entry in self.productList.values()))


            else:
                self.showAlert("Error 1 occured, try again later")

        else:
            self.showAlert("You have to fill all fields")

    def change_discount(self):
        added_discount = self.ids.discount.text
        self.ids.discount.text = ''
        if (added_discount == '' or added_discount == None):
            self.notify.add_widget(Label(text='[color=#FF0000][b] Enter valid Input[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)
        else:

            for item in self.listofKeys:
                thequantity = self.productList[item][3]
                thecash = self.productList[item][2]

                multiplied = float(thequantity) * float(thecash)
                self.thesumsList.append(multiplied)

            self.ids.thetotal.text = "Total Payable: " + str( sum(float(entry[2]) * float(entry[3]) for entry in self.productList.values()) - (float(added_discount) * 1))
            self.final_Amount = sum( float(entry[2]) * float(entry[3]) for entry in self.productList.values()) - (float(added_discount) * 1)
            self.showAlert("Discount Added")

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
        self.ids.cur_price.text = "KES: " + resultantList[2]
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
        pass

    def on_age(self, *args):
        self.str_age = "Age: {}".format(self.age)

    def clearWidgets(self):
        self.ids.receipt_Preview.clear_widgets()
        self.thesumsList.clear()
        self.complete_total = 0.00
        self.ids.cur_price.text = "0.0"
        self.ids.cur_product.text = "Default Product"
        self.ids.thetotal.text = "Total: 0.0"
        self.final_Amount = 0.0
        self.ids.thebalance.text = 'Bal: 0.0'
        self.ids.mpesacode.text = ''
        self.ids.amountinput.text = ''
        target = self.ids.thebox
        target.clear_widgets()

    def logout(self):
        target = self.ids.thebox
        target.clear_widgets()
        self.thesumsList.clear()
        self.complete_total = 0.00
        self.ids.cur_price.text = "0.0"
        self.ids.cur_product.text = "Default Product"
        self.ids.thetotal.text = "Total: 0.0"
        self.final_Amount = 0.0
        self.ids.thebalance.text = 'Bal: 0.0'
        self.ids.mpesacode.text = ''
        self.ids.amountinput.text = ''
        self.parent.parent.current = 'scrn_login'


    def getproductList(self):
        toPrintA = '{:>15} {:>10} {:>10}'.format("Item", "Qty", "Amount")
        toPrintB = []

        for key, values in self.productList.items():
            toPrintB.append('{:>15} {:>10} {:>10}'.format(key, values[3], values[2]))

        assin = '\n'.join(map(str, toPrintB))

        return toPrintA + "\n" + assin



    def print_output(self):

        if any(self.productList) == False:
            self.notify.add_widget(Label(text='[color=#FF0000][b]Add Items to cart first[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)
        else:

            self.clearWidgets()

            # Item already exists, try and get the name of the text
            thetext = self.ids.thetotal.text
            # Split on colon
            thetext_splitted = thetext.split(":")
            # Get last value (strip() removes spaces)
            last_value = thetext_splitted[-1].strip()

            if(self.payment_Mode == ''):
                self.notify.add_widget(Label(text='[color=#FF0000][b] Enter Mode Of Pay[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 5)

            else:
                companyName = "Hilton Steel and Cement"
                paytype = self.payment_Mode
                companyName = companyName + "\n\nSale Receipt\n\nOpp Golden Line Mall\nP.O BOX 3404-20100\nTEL: 0727441192\nEMAIL: Hiltonltd@yandex.com"
                receiptNo = randint(1, 100000)
                finalString = companyName + "\n\nReceipt No:" + str(receiptNo) + "\n\n" + self.getproductList()\
                              + "\n____________________________\n" + "Total Due:        " + str(self.totaltoBePaid)  + "\n____________________________\n\n" + "Paid In:     " + paytype + "\n\n"+ "Served By:     " + str(self.user) +"\n" + "Payment:           " + str(self.finalvariables[1])+ "\nBalance:            " + str(self.finalvariables[0])  + "\n\n\nWelcome Back"


                for key, values in self.productList.items():

                    code = values[1]
                    quantity = values[3]

                    #Load its current number using the code first
                    # Validate this product firs
                    mycursor.execute("SELECT * FROM products WHERE code=%s and location=%s", (code, self.reallocation))
                    data = mycursor.fetchone()

                    if (data):
                        stock = data[6]
                        newstock = float(stock) - float(quantity)
                        #Insert the new stock data into the database table
                        mycursor.execute("""UPDATE products SET stock=%s WHERE stock=%s and location=%s""",(newstock, stock, self.reallocation))
                        db.commit()

                    else:
                        self.showAlert('Operation Incomplete, Code Error')


                self.productList.clear()
                self.customerbalance = ''
                self.customerpayed = ''
                self.finalvariables.clear()

                open(self.filename, "w").write(finalString)
                os.startfile(self.filename, "print")


class PosApp(App):

    def build(self):
        return PosWindow()


if __name__ == "__main__":
    sa = PosApp()
    sa.run()