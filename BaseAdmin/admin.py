from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

Config.set('graphics', 'resizable', False)
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from utils.usersrecycler import DataTable
import pyrebase

Builder.load_file('BaseAdmin/admin.kv')


class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.3, .3)


class AdminWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cred = credentials.Certificate('privatekey.json')

        firebase_admin.initialize_app(self.cred, {
            'databaseURL': 'https://cocabpos-e5199.firebaseio.com/'
        })

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

        content = self.ids.scrn_contents
        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

        productContents = self.ids.scrn_product_contents
        products = self.get_products()
        productstable = DataTable(products)
        productContents.add_widget(productstable)

        salesContents = self.ids.display_sales
        sales = self.get_sales()
        salestable = DataTable(sales)
        salesContents.add_widget(salestable)

    def search_Field(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        self.crud_search_word = TextInput(hint_text='Enter Product Code || Product name')
        # Load the values from the database
        crud_search_criteria = Spinner(text='code', values=['code', 'name'])
        crud_submit = Button(text='Search', size_hint_x=None, width=100,
                             on_release=lambda x: self.dotheSearch(self.crud_search_word.text, crud_search_criteria.text))

        target.add_widget(self.crud_search_word)
        target.add_widget(crud_search_criteria)
        target.add_widget(crud_submit)

    def dotheSearch(self, searchWord, searchCriteria):
        content = self.ids.display_searched_products
        content.clear_widgets()

        chosenCriteria = ''

        if searchCriteria == '' or searchWord == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:

            if searchCriteria == 'code':
                chosenCriteria = 'code'
            elif searchCriteria == 'name':
                chosenCriteria = "name"

        ref = db.reference('products')
        snapshot = ref.order_by_child(chosenCriteria).start_at(searchWord).end_at(searchWord + "\uf8ff").get()

        name = [value['name'] for value in snapshot.values()]
        code = [value['code'] for value in snapshot.values()]
        buyingprice = [value['buyingprice'] for value in snapshot.values()]
        sellingprice = [value['sellingprice'] for value in snapshot.values()]
        category = [value['category'] for value in snapshot.values()]

        _products = dict()
        _products['name'] = {}
        _products['code'] = {}
        _products['buyingprice'] = {}
        _products['sellingprice'] = {}
        _products['category'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _products['name'][idx] = name[idx]
            _products['code'][idx] = code[idx]
            _products['buyingprice'][idx] = buyingprice[idx]
            _products['sellingprice'][idx] = sellingprice[idx]
            _products['category'][idx] = category[idx]

            idx += 1

        # Change Screen
        self.ids.scrn_mngr.current = 'screen_search_product'

        productContents = self.ids.display_searched_products
        productstable = DataTable(_products)
        productContents.add_widget(productstable)
        print(productstable)

        self.crud_search_word.text = ''

    def view_categories(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        prods = self.db.child("categorylist").get().val()

        # Load the values from the database
        crud_category = Spinner(text='Select', values=prods.values())
        crud_submit = Button(text='View', size_hint_x=None, width=100,
                             on_release=lambda x: self.show_product_in_chosen_categories(crud_category.text))

        target.add_widget(crud_category)
        target.add_widget(crud_submit)

    def show_product_in_chosen_categories(self, crud_category):

        content = self.ids.display_categorized_products
        content.clear_widgets()

        self.users = self.ref.child("products").order_by_child("category").equal_to(crud_category).get()

        name = [value['name'] for value in self.users.values()]
        code = [value['code'] for value in self.users.values()]
        buyingprice = [value['buyingprice'] for value in self.users.values()]
        sellingprice = [value['sellingprice'] for value in self.users.values()]
        category = [value['category'] for value in self.users.values()]

        _products = dict()
        _products['name'] = {}
        _products['code'] = {}
        _products['buyingprice'] = {}
        _products['sellingprice'] = {}
        _products['category'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _products['name'][idx] = name[idx]
            _products['code'][idx] = code[idx]
            _products['buyingprice'][idx] = buyingprice[idx]
            _products['sellingprice'][idx] = sellingprice[idx]
            _products['category'][idx] = category[idx]

            idx += 1

        # Change Screen
        self.ids.scrn_mngr.current = 'scrn_product_categorized'

        productContents = self.ids.display_categorized_products
        productstable = DataTable(_products)
        productContents.add_widget(productstable)
        print(productstable)

    def remove_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        self.crud_code = TextInput(hint_text='Product Code')
        crud_submit = Button(text='Remove', size_hint_x=None, width=100,
                             on_release=lambda x: self.remove_product(self.crud_code.text))

        target.add_widget(self.crud_code)
        target.add_widget(crud_submit)

    def remove_product(self, code):

        if code == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            self.db.child("products").child(code).remove()

        content = self.ids.scrn_product_contents
        content.clear_widgets()
        self.crud_code.text = ''

        prodz = self.get_products()
        stocktable = DataTable(table=prodz)
        content.add_widget(stocktable)

    def update_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        crud_code = TextInput(hint_text='Product Code', multiline=False, write_tab=False)
        crud_name = TextInput(hint_text='Product Name', multiline=False, write_tab=False)
        crud_buyingprice = TextInput(hint_text='Buying Price', multiline=False, write_tab=False)
        crud_selling_price = TextInput(hint_text='Selling Price', multiline=False, write_tab=False)

        prods = self.db.child("categorylist").get().val()
        print(prods)
        # Load the values from the database
        crud_category = Spinner(text='Prod Category', values=prods.values())
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_product(crud_code.text, crud_name.text,
                                                                   crud_buyingprice.text, crud_selling_price.text,
                                                                   crud_category.text))

        target.add_widget(crud_code)
        target.add_widget(crud_name)
        target.add_widget(crud_buyingprice)
        target.add_widget(crud_selling_price)
        target.add_widget(crud_category)
        target.add_widget(crud_submit)

    def update_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        self.crud_code = TextInput(hint_text='Product Code', multiline=False, write_tab=False)
        self.crud_name = TextInput(hint_text='Product Name', multiline=False, write_tab=False)
        self.crud_buyingprice = TextInput(hint_text='Buying Price', multiline=False, write_tab=False)
        self.crud_selling_price = TextInput(hint_text='Selling Price', multiline=False, write_tab=False)

        prods = self.db.child("categorylist").get().val()
        print(prods)
        # Load the values from the database
        crud_category = Spinner(text='Prod Category', values=prods.values())
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.update_product(self.crud_code.text, self.crud_name.text,
                                                                      self.crud_buyingprice.text, self.crud_selling_price.text,
                                                                      crud_category.text))

        target.add_widget(self.crud_code)
        target.add_widget(self.crud_name)
        target.add_widget(self.crud_buyingprice)
        target.add_widget(self.crud_selling_price)
        target.add_widget(crud_category)
        target.add_widget(crud_submit)

    def update_product(self, code, name, buyingprice, sellingprice, category):

        x = name
        y = ("-".join(x.split()))

        datte = {}
        datte["code"] = code
        datte["name"] = y
        datte["buyingprice"] = buyingprice
        datte["sellingprice"] = sellingprice
        datte["category"] = category

        if code == '' or name == '' or buyingprice == '' or sellingprice == '' or category == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)

        else:
            self.db.child("products").child(code).set(datte)

        content = self.ids.scrn_product_contents
        content.clear_widgets()

        self.crud_code.text = ''
        self.crud_name.text = ''
        self.crud_buyingprice.text = ''
        self.crud_selling_price.text = ''
        self.crud_code.text = ''
        self.crud_code.text = ''

        users = self.get_products()
        userstable = DataTable(table=users)
        content.add_widget(userstable)


    def add_product_category_field(self):

        target = self.ids.ops_fields_p
        target.clear_widgets()

        self.categoryName = TextInput(hint_text='Name of the category', multiline=False, write_tab=False)
        crud_submit = Button(text='Add Product', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_product_category(self.categoryName.text))

        target.add_widget(self.categoryName)
        target.add_widget(crud_submit)

    def add_product_category(self, categoryName):

        if categoryName == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)

        else:
            self.db.child("categorylist").push(categoryName)


        # content = self.ids.scrn_product_contents
        # content.clear_widgets()

        self.categoryName.text = ''

    def change_screen(self, instance):

        if instance.text == 'Manage Products':
            self.ids.scrn_mngr.current = 'scrn_product_content'

        elif instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content_manage_users'

        elif instance.text == 'Point Of Sale':
            self.parent.parent.current = 'scrn_pos'

        elif instance.text == 'Sales':
            self.ids.scrn_mngr.current = 'screen_display_sales'
        else:
            pass

    def add_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        self.crud_code = TextInput(hint_text='Product Code', multiline=False, write_tab=False)
        self.crud_name = TextInput(hint_text='Product Name', multiline=False, write_tab=False)
        self.crud_buyingprice = TextInput(hint_text='Buying Price', multiline=False, write_tab=False)
        self.crud_selling_price = TextInput(hint_text='Selling Price', multiline=False, write_tab=False)

        prods = self.db.child("categorylist").get().val()
        print(prods)
        # Load the values from the database
        crud_category = Spinner(text='Prod Category', values=prods.values())
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_product(self.crud_code.text, self.crud_name.text,
                                                                   self.crud_buyingprice.text, self.crud_selling_price.text,
                                                                   crud_category.text))

        target.add_widget(self.crud_code)
        target.add_widget(self.crud_name)
        target.add_widget(self.crud_buyingprice)
        target.add_widget(self.crud_selling_price)
        target.add_widget(crud_category)
        target.add_widget(crud_submit)

    def add_product(self, code, name, buyingprice, sellingprice, category):
        x = name
        y = ("-".join(x.split()))

        datte = {}
        datte["code"] = code
        datte["name"] = y
        datte["buyingprice"] = buyingprice
        datte["sellingprice"] = sellingprice
        datte["category"] = category

        if code == '' or name == '' or buyingprice == '' or sellingprice == '' or category == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)

        else:
            self.db.child("products").child(code).set(datte)

        content = self.ids.scrn_product_contents
        content.clear_widgets()

        #Empty the widgets
        self.crud_code.text = ''
        self.crud_name.text = ''
        self.crud_buyingprice.text = ''
        self.crud_selling_price.text = ''

        users = self.get_products()
        userstable = DataTable(table=users)
        content.add_widget(userstable)


    def remove_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        self.user = TextInput(hint_text='Id Number')
        crud_submit = Button(text='Remove', size_hint_x=None, width=100,
                             on_release=lambda x: self.remove_user(self.user.text))

        target.add_widget(self.user)
        target.add_widget(crud_submit)

    def remove_user(self, user):

        if user == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            self.db.child("users").child(user).remove()

        self.user.text = ''
        content = self.ids.scrn_contents
        content.clear_widgets()

        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

    def update_user_fields(self):

        target = self.ids.ops_fields
        target.clear_widgets()

        self.name = TextInput(hint_text='Both Names', multiline=False, write_tab=False)
        self.theid = TextInput(hint_text='id', multiline=False, write_tab=False)
        self.mobile = TextInput(hint_text='Mobile', multiline=False, write_tab=False)
        designation = Spinner(text='Operator', values=['Operator', 'Administrator'])
        crud_submit = Button(text='Update', size_hint_x=None, width=100,
                             on_release=lambda x: self.update_user(self.name.text, self.theid.text, designation.text,
                                                                   self.mobile.text))

        target.add_widget(self.name)
        target.add_widget(self.theid)
        target.add_widget(designation)
        target.add_widget(self.mobile)
        target.add_widget(crud_submit)

    def update_user(self, name, id, mobile, designation):

        if name == '' or id == '' or mobile == '' or designation == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)

        else:

            datte = {}
            datte["name"] = name
            datte["mobile"] = mobile
            datte["id"] = id
            datte["designation"] = designation

            self.db.child("users").child(id).set(datte)

            content = self.ids.scrn_contents
            content.clear_widgets()

            users = self.get_users()
            userstable = DataTable(table=users)
            content.add_widget(userstable)

            # Empty the widgets
            self.name.text = ''
            self.theid.text = ''
            self.mobile.text = ''

    def add_user_fields(self):

        target = self.ids.ops_fields
        target.clear_widgets()

        self.bothnames = TextInput(hint_text='Both Names', multiline=False, write_tab=False)
        self.mobile = TextInput(hint_text='Email', multiline=False, write_tab=False)
        self.idnumber = TextInput(hint_text='Id Number', multiline=False, write_tab=False)
        designation = Spinner(text='Operator', values=['Operator', 'Administrator'])

        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_user(self.bothnames.text, self.mobile.text, self.idnumber.text,designation.text))

        target.add_widget(self.bothnames)
        target.add_widget(self.mobile)
        target.add_widget(self.idnumber)
        target.add_widget(designation)
        target.add_widget(crud_submit)

    def add_user(self, bothnames, mobile, idnumber, designation):

        datte = {}
        datte["name"] = bothnames
        datte["mobile"] = mobile
        datte["id"] = idnumber
        datte["designation"] = designation

        if (bothnames == '' or mobile == '' or idnumber == '' or designation == ''):
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            self.db.child("users").child(idnumber).set(datte)
            user = self.auth.create_user_with_email_and_password(mobile, idnumber)


        content = self.ids.scrn_contents
        content.clear_widgets()

        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

        self.bothnames.text = ''
        self.mobile.text = ''
        self.idnumber.text = ''

    def get_users(self):

        self.firebaseconfig = {
            "apiKey": "AIzaSyDGsXv0wa7Fc4irPi3MX_uWTIfuWHeEIzU",
            "authDomain": "projectId.firebaseapp.com",
            "databaseURL": "https://cocabpos-e5199.firebaseio.com/",
            "storageBucket": "projectId.appspot.com"
        }

        self.firebase = pyrebase.initialize_app(self.firebaseconfig)
        self.auth = self.firebase.auth()

        self.db = self.firebase.database()

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

        _users = dict()
        _users['name'] = {}
        _users['mobile'] = {}
        _users['id'] = {}
        _users['designation'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _users['name'][idx] = name[idx]
            _users['mobile'][idx] = mobile[idx]
            _users['id'][idx] = id[idx]
            _users['designation'][idx] = designation[idx]

            idx += 1

        return _users

    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def get_sales(self):

        self.sales = self.db.child("sales").get()
        name = []
        date = []
        payment = []
        number = []

        for sale in self.sales.each():
            key = sale.key()

            retrieve_amount = self.db.child("sales").child(key).child("amount").get().val()
            name.append(retrieve_amount)

            retrieve_date = self.db.child("sales").child(key).child("date").get().val()
            date.append(retrieve_date)

            retrieve_payment = self.db.child("sales").child(key).child("payment").get().val()
            payment.append(retrieve_payment)

            retrieve_number = self.db.child("sales").child(key).child("number").get().val()
            number.append(retrieve_number)

        _sales = dict()
        _sales['name'] = {}
        _sales['date'] = {}
        _sales['payment'] = {}
        _sales['number'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _sales['name'][idx] = name[idx]
            _sales['date'][idx] = date[idx]
            _sales['payment'][idx] = payment[idx]
            _sales['number'][idx] = number[idx]

            idx += 1

        return _sales

    def get_products(self):

        self.users = self.db.child("products").get()
        name = []
        code = []
        buyingprice = []
        sellingprice = []
        category = []

        for user in self.users.each():
            key = user.key()

            retrieve_name = self.db.child("products").child(key).child("name").get().val()
            name.append(retrieve_name)

            retrieve_mobile = self.db.child("products").child(key).child("code").get().val()
            code.append(retrieve_mobile)

            retrieve_id = self.db.child("products").child(key).child("buyingprice").get().val()
            buyingprice.append(retrieve_id)

            retrieve_designation = self.db.child("products").child(key).child("sellingprice").get().val()
            sellingprice.append(retrieve_designation)

            retrieve_category = self.db.child("products").child(key).child("category").get().val()
            sellingprice.append(retrieve_category
                                )

        _products = dict()
        _products['name'] = {}
        _products['code'] = {}
        _products['buyingprice'] = {}
        _products['sellingprice'] = {}
        _products['category'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _products['name'][idx] = name[idx]
            _products['code'][idx] = code[idx]
            _products['buyingprice'][idx] = buyingprice[idx]
            _products['sellingprice'][idx] = sellingprice[idx]
            _products['category'][idx] = sellingprice[idx]

            idx += 1

        return _products

    def searchForTheDates(self):

        content = self.ids.display_sales
        content.clear_widgets()

        result_thesales = self.ids.the_sales.text

        if result_thesales == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            ref = db.reference('sales')
            snapshot = ref.order_by_child('date').start_at(result_thesales).end_at(result_thesales + "\uf8ff").get()

            payment = [value['payment'] for value in snapshot.values()]
            date = [value['date'] for value in snapshot.values()]
            amount = [value['amount'] for value in snapshot.values()]
            number = [value['number'] for value in snapshot.values()]

            _sales = dict()
            _sales['payment'] = {}
            _sales['date'] = {}
            _sales['amount'] = {}
            _sales['number'] = {}

            users_length = len(amount)
            idx = 0

            while idx < users_length:
                _sales['payment'][idx] = payment[idx]
                _sales['date'][idx] = date[idx]
                _sales['amount'][idx] = amount[idx]
                _sales['number'][idx] = number[idx]

                idx += 1

            # Change Screen
            self.ids.scrn_mngr.current = 'screen_display_sales'

            secondSales = self.ids.display_sales
            thesalesresults = DataTable(_sales)
            secondSales.add_widget(thesalesresults)

class AdminApp(App):
    def build(self):
        return AdminWindow()


if __name__ == "__main__":
    active_App = AdminApp()
    active_App.run()
