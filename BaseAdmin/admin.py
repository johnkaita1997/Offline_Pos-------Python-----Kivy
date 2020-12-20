import datetime
import os
import tempfile
from random import randint

import fpdf
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

import overall

Config.set('graphics', 'resizable', False)
from kivy.lang import Builder
from utils.usersrecycler import DataTable
from testmysql import mycursor, db
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
import pandas as pd
from tkinter.filedialog import askopenfilename
from tkinter import Tk
Builder.load_file('BaseAdmin/admin.kv')

class TextInputPopup(Popup):
    obj = ObjectProperty(None)
    obj_text = StringProperty("")

    def __init__(self, obj, **kwargs):
        super(TextInputPopup, self).__init__(**kwargs)
        self.obj = obj
        self.obj_text = obj.text


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''

class SelectableButton(RecycleDataViewBehavior, Button):
    ''' Add selection support to the Button '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    rv = None

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableButton, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableButton, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        self.index = index
        self.rv = rv

    def on_press(self):
        popup = TextInputPopup(self)
        popup.open()

    def get_row_range(self, index: int, num_cols: int) -> range:
        # index - index, which you want the row of
        # num_cols - number of columns in your table
        row = int(index / num_cols)  # the row you want
        return range(row * num_cols, (row + 1) * num_cols)  # the range which that index lies


    def update_changes(self, txt, spinnerinput, obj_text):
        # ALERT DIALOG IN  PYTHO
        hello = AdminWindow()
        # Example usage of querying the index '10'
        clicked_index = self.index # in the event handler get which index was clicked
        num_cols = 9  # your example has 9 columns

        #List
        thelist = []

        for i in self.get_row_range(clicked_index, num_cols):
            thelist.append(self.rv.data[i]["text"])

        buyingprice = thelist[0]
        category = thelist[1]
        code = thelist[2]
        name = thelist[3]
        sellingprice = thelist[4]
        availability = thelist[5]
        stock = thelist[6]
        choose = thelist[7]
        location = thelist[8]

        try:
            # insert intio the database

            mycursor.execute("""select * from products where id = %s and location=%s""", (choose, overall.location))
            data = mycursor.fetchall()

            if data:
                for sale in data:

                    got_Stock = sale[6]
                    new_Stock = float(got_Stock) + float(txt)
                    print(str(got_Stock), str(txt))

                    mycursor.execute("""UPDATE products SET stock=%s, availabilitiy=%s WHERE id=%s and location =%s""",
                                     (str(new_Stock), spinnerinput, choose, overall.location))
                    db.commit()
            else:
                hello.showAlert("Product not found")


        except Exception as erro:
            hello.showAlert(str(erro))
        else:
            hello.showAlert("Operation was successful")


class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.3, .3)


class AdminWindow(BoxLayout):
    data_items = ListProperty([])
    mylocation = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.notify = Notify()
        self.blob_value = None
        self.filename = tempfile.mktemp(".txt")

    def fetchInvoice(self):
        target = self.ids.ops_fields_invoice
        target.clear_widgets()

        self.uclientcode = TextInput(hint_text='clientcode', multiline=False, write_tab=False)
        self.ucompanyname = TextInput(hint_text='TO: Name', multiline=False, write_tab=False)
        self.ucompanymobile = TextInput(hint_text='TO: Mobile', multiline=False, write_tab=False)
        crud_submit = Button(text='Print Invoice', size_hint_x=None, width=100,
                             on_release=lambda x: self.actualInvoice(self.ucompanyname.text, self.ucompanymobile.text, self.uclientcode.text))

        target.add_widget(self.uclientcode)
        target.add_widget(self.ucompanyname)
        target.add_widget(self.ucompanymobile)
        target.add_widget(crud_submit)

    def actualInvoice(self, mcompanyname, mcompanymobile, mclientcode):
        if mcompanyname == '' or mcompanymobile == '' or mclientcode == '':
            self.showAlert("Enter all fields")
        else:

            confirmedname = mcompanyname
            confirmedmobile = mcompanymobile
            confirmedclientcode = mclientcode

            beginday = self.sgday
            beginmonth = self.sgmonth
            beginyear = self.sgyear

            endday = self.egday
            endmonth = self.egmonth
            endyear = self.egyear

            mindate = beginyear + "-" + beginmonth + "-" + beginday
            maxdate = endyear + "-" + endmonth + "-" + endday

            datte = {}
            datte['mindate'] = mindate
            datte['maxdate'] = maxdate

            editedmindate = datetime.datetime.strptime(mindate, '%Y-%m-%d')
            editedmaxdate = datetime.datetime.strptime(maxdate, '%Y-%m-%d')

            print(editedmaxdate, editedmindate)

            mycursor.execute(
                """select * from sales where date <= %s and date >= %s and location=%s and confirmationcode =%s""",
                (editedmaxdate, editedmindate, self.mylocation, confirmedclientcode))
            data = mycursor.fetchall()

            if data:
                date = []
                amount = []
                payment = []
                served = []
                location = []
                confirmationcode = []
                customerpay = []
                balance = []

                total = str(sum(float(sale[4])for sale in data))

                for sale in data:
                    retrieve_date = sale[0]
                    date.append(retrieve_date)

                    retrieve_amount = sale[4]
                    amount.append(retrieve_amount)

                    retrieve_payment = sale[6]
                    payment.append(retrieve_payment)

                    retrieve_served = sale[7]
                    served.append(retrieve_served)

                    retrieve_location = sale[8]
                    location.append(retrieve_location)

                    retrieve_confirmationcode = sale[11]
                    confirmationcode.append(retrieve_confirmationcode)

                    retrieve_customerpay = sale[9]
                    customerpay.append(retrieve_customerpay)

                    retrieve_balance = sale[10]
                    balance.append(retrieve_balance)

                _sales = dict()
                _sales['Date'] = {}
                _sales['Amount'] = {}
                _sales['Payment'] = {}
                _sales['Served'] = {}
                _sales['Location'] = {}
                _sales['Code'] = {}
                _sales['Customerpay'] = {}
                _sales['Balance'] = {}

                users_length = len(date)
                idx = 0
                while idx < users_length:
                    _sales['Date'][idx] = date[idx]
                    _sales['Amount'][idx] = amount[idx]
                    _sales['Payment'][idx] = payment[idx]
                    _sales['Served'][idx] = served[idx]
                    _sales['Location'][idx] = location[idx]
                    _sales['Code'][idx] = confirmationcode[idx]
                    _sales['Customerpay'][idx] = customerpay[idx]
                    _sales['Balance'][idx] = balance[idx]

                    idx += 1

                # Change the text values
                self.ids.total_sales_select.text = "TOT SALES: KES:" + " " + total

                target = self.ids.ops_fields_invoice
                target.clear_widgets()

                # Change Screen
                content = self.ids.display_sales
                content.clear_widgets()
                salestable = DataTable(_sales)
                content.add_widget(salestable)

                self.uclientcode.text = ''
                self.ucompanyname.text = ''
                self.ucompanymobile.text = ''

                from_Company = 'Hilton Steel and Cement'
                address = 'P.O Box 3404-20100'
                city = 'Nakuru'
                tel_no = '0727441192'
                email = 'Hiltonltd@yandex.com '
                date = str(datetime.datetime.today())
                invoiceno = str(randint(1, 10000))
                header = "                                     COMPANY INVOICE\n\n\n\n"
                clientname = confirmedname
                clientmobile = confirmedmobile
                thedata = pd.DataFrame(_sales)
                ending = "SUB TOTALS:       KES " + total + "\nVAT(14%):         KES " +   str( int((sum(float(sale[4]) for sale in data)) * 0.14)) + ".0" + "\nINVOICE TOTALS:   KES " + str(sum(float(sale[4])for sale in data) - (0.14 * (sum(float(sale[4])for sale in data))))
                print(_sales)
                left_aligned = header + "\nCOMPANY: " + from_Company + '                                    DATE: ' + date + '\n                                                                    INVOICE NO: ' + invoiceno + "\nADDRESS: " + address + "\nCITY :" + city + "\nEMAIL: " + email + "\nTEL NO: " + tel_no + "\nVAT NO: " + " " + "\n\n\n\nBILL TO:" + clientname + '\nTEL NO: ' + clientmobile + "\n\n\n"
                open(self.filename, "w").write(left_aligned + str(thedata) + "\n\n\n\n\n" + ending)
                os.startfile(self.filename, "print")

            else:
                self.showAlert("No records")

    def remove_branch_fields(self):
        target = self.ids.ops_fields_branches
        target.clear_widgets()
        self.brachnamed = TextInput(hint_text='Brach Name')
        crud_submit = Button(text='Remove', size_hint_x=None, width=100,
                             on_release=lambda x: self.remove_branch(self.brachnamed.text))

        target.add_widget(self.brachnamed)
        target.add_widget(crud_submit)


    def remove_branch(self, branch):
        if branch == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Enter Brach Name[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)
        else:

            # ALERT DIALOG IN  PYTHON
            try:
                mycursor.execute("DELETE FROM braches WHERE name=%s", (branch,))
                db.commit()
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

        content = self.ids.scrn_branches
        content.clear_widgets()

        branches = self.get_branches()
        branchestable = DataTable(table=branches)
        content.add_widget(branchestable)

        self.brachnamed.text = ''


    def add_branch_fields(self):
        target = self.ids.ops_fields_branches
        target.clear_widgets()

        self.branchname = TextInput(hint_text='Branch Name', multiline=False, write_tab=False)
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_branch(self.branchname.text))

        target.add_widget(self.branchname)
        target.add_widget(crud_submit)

    def add_branch(self, bothnames):
        datte = {}
        datte["name"] = bothnames

        if (bothnames == ''):
            self.notify.add_widget(Label(text='[color=#FF0000][b]Enter the branch name[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)
        else:
            try:
                mycursor.execute("""INSERT INTO braches (name)  VALUES (%(name)s)""", datte)
                db.commit()
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

        content = self.ids.scrn_branches
        content.clear_widgets()

        branches = self.get_branches()
        branchestable = DataTable(table=branches)
        content.add_widget(branchestable)

        self.branchname.text = ''

    def print_special_receipt(self):
        #Get the transaction code
        ztransactioncode = self.ids.transactioncode.text
        if ztransactioncode:
            #Load from the database sale with that transaction code
            mycursor.execute("SELECT * FROM sales WHERE confirmationcode=%s", (ztransactioncode,))
            data = mycursor.fetchall()

            if data:
                for sale in data:
                     date = sale[0]
                     month = sale[1]
                     year = sale[2]
                     day = sale[3]
                     amount = sale[4]
                     number = sale[5]
                     payment = sale[6]
                     served = sale[7]
                     location = sale[8]
                     customerpay = sale[9]
                     balance = sale[10]
                     confirmationcode = sale[11]
                     products = str(sale[13])

                     print(amount)

                companyName = "Hilton Steel and Cement"
                paytype = payment
                companyName = companyName + "\n\nSale Receipt\n\nOpp Golden Line Mall\nP.O BOX 0000\nTEL:0727441192\nEMAIL: cocabtechsolutions@gmail.com"
                receiptNo = randint(1, 100000)
                finalString = companyName + "\n\nReceipt No:" + str(receiptNo) + "\n\n" + products \
                              + "\n______________________________________\n" + "Total Due:        " + amount + "\n______________________________________\n\n" + "Paid In:     " + paytype + "\n\n" + "Served By:     " + served + "\n" + "Payment:           " +  customerpay + "\nBalance:            " + balance + "\n\n\nWelcome Back"

                open(self.filename, "w").write(finalString)
                os.startfile(self.filename, "print")


            else:
                self.showAlert("No such entry.\n    Check your code")

            self.ids.transactioncode.text = ''
        else:
            self.showAlert("Enter the transaction code")



    def refresh_branches(self):
        content = self.ids.scrn_branches
        content.clear_widgets()
        branches = self.get_branches()
        branchestable = DataTable(table=branches)
        content.add_widget(branchestable)

    def loadEverything(self):

        self.filename = tempfile.mktemp(".txt")

        overall.location = self.mylocation

        content = self.ids.scrn_contents
        content.clear_widgets()

        content = self.ids.scrn_product_contents
        content.clear_widgets()

        content = self.ids.display_sales
        content.clear_widgets()

        content = self.ids.scrn_branches
        content.clear_widgets()

        # Load the recyclerview
        self.get_users_new()

        content = self.ids.scrn_contents
        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

        content = self.ids.scrn_branches
        branches = self.get_branches()
        branchestable = DataTable(table=branches)
        content.add_widget(branchestable)

        productContents = self.ids.scrn_product_contents
        products = self.get_products()
        productstable = DataTable(products)
        productContents.add_widget(productstable)

        salesContents = self.ids.display_sales
        sales = self.get_sales()
        salestable = DataTable(sales)
        salesContents.add_widget(salestable)

        self.loadspinners()
        self.loadtheinitiator()

        self.overalldata = {}


    def refreshRecyclerView(self):
        # Load the recyclerview
        self.get_users_new()

    def searchInventory(self):
        input = self.ids.nipe.text
        if input:
            mycursor.execute("SELECT buyingprice, category, code, name, sellingprice, availabilitiy, stock, id, location FROM products WHERE code LIKE %s or name LIKE %s and location = %s",
                             ( "%" + input + "%", "%" + input + "%", self.mylocation))
            data = mycursor.fetchall()

            if data:
                self.data_items = []
                arrows = str(mycursor.rowcount)
                self.ids.total_inventory.text = arrows + " Products"
                # create data_items
                for row in data:
                    for col in row: \
                            self.data_items.append(col)
            else:
                self.showAlert("Couldn't find such record")

        else:
            mycursor.execute(
                "SELECT buyingprice, category, code, name, sellingprice, availabilitiy, stock, id, location FROM products WHERE  location = %s",
                (self.mylocation,))
            data = mycursor.fetchall()

            if data:
                self.data_items = []
                arrows = str(mycursor.rowcount)
                self.ids.total_inventory.text = arrows + " Products"
                # create data_items
                for row in data:
                    for col in row: \
                            self.data_items.append(col)


    def choose(self):
        # Select image file types, returned image should be used as source of Image widget.
        Tk().withdraw()  # avoids window accompanying tkinter FileChooser
        path = askopenfilename(initialdir="/", title="Select file",
                               filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))

        try:
            thedata = open(path, 'rb').read()
            self.blob_value = thedata
        except:
            pass

    def export_Sales(self):
        sales = self.salesForToday()
        data = pd.DataFrame(sales)

        datatoExcel = pd.ExcelWriter("C:\CocabTechSolutionsPos\Sales.xlsx", engine='xlsxwriter')
        data.to_excel(datatoExcel, sheet_name='Sheet1')
        datatoExcel.save()

        text_file = open("C:\CocabTechSolutionsPos\Sales.txt", "w")
        text_file.write("Purchase Amount: %s" % data)
        text_file.close()

        pdf = fpdf.FPDF(format='letter')
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.write(5, str(data))
        pdf.ln()
        pdf.output("C:\CocabTechSolutionsPos\Sales.pdf")

    def print_sales(self):
        sales = self.get_sales()
        data = pd.DataFrame(sales)
        open(self.filename, "w").write(str(data))
        os.startfile(self.filename, "print")


    def salesForToday(self):
        d4 = datetime.datetime.today().strftime("%Y-%m-%d")
        mycursor.execute("SELECT * FROM sales WHERE location=%s and date=%s", (self.mylocation, d4))
        data = mycursor.fetchall()
        date = []
        amount = []
        payment = []
        served = []
        location = []
        confirmationcode = []
        customerpay = []
        balance = []

        self.overalldata = data

        for sale in data:
            retrieve_date = sale[0]
            date.append(retrieve_date)

            retrieve_amount = sale[4]
            amount.append(retrieve_amount)

            retrieve_payment = sale[6]
            payment.append(retrieve_payment)

            retrieve_served = sale[7]
            served.append(retrieve_served)

            retrieve_location = sale[8]
            location.append(retrieve_location)

            retrieve_confirmationcode = sale[11]
            confirmationcode.append(retrieve_confirmationcode)

            retrieve_customerpay = sale[9]
            customerpay.append(retrieve_customerpay)

            retrieve_balance = sale[10]
            balance.append(retrieve_balance)

        _sales = dict()
        _sales['Date'] = {}
        _sales['Amount'] = {}
        _sales['Payment'] = {}
        _sales['Served'] = {}
        _sales['Location'] = {}
        _sales['Code'] = {}
        _sales['Customerpay'] = {}
        _sales['Balance'] = {}

        users_length = len(date)
        idx = 0
        while idx < users_length:
            _sales['Date'][idx] = date[idx]
            _sales['Amount'][idx] = amount[idx]
            _sales['Payment'][idx] = payment[idx]
            _sales['Served'][idx] = served[idx]
            _sales['Location'][idx] = location[idx]
            _sales['Code'][idx] = confirmationcode[idx]
            _sales['Customerpay'][idx] = customerpay[idx]
            _sales['Balance'][idx] = balance[idx]

            idx += 1

        return _sales


    def exportInventory(self):
        sales = self.get_products()
        data = pd.DataFrame(sales)

        datatoExcel = pd.ExcelWriter("C:\CocabTechSolutionsPos\Inventory.xlsx", engine='xlsxwriter')
        data.to_excel(datatoExcel, sheet_name='Sheet1')
        datatoExcel.save()

        text_file = open("C:\CocabTechSolutionsPos\Inventory.txt", "w")
        text_file.write("Purchase Amount: %s" % data)
        text_file.close()

        pdf = fpdf.FPDF(format='letter')
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.write(5, str(data))
        pdf.ln()
        pdf.output("C:\CocabTechSolutionsPos\Inventory.pdf")


    def printInventory(self):
        sales = self.get_products()
        data = pd.DataFrame(sales)
        open(self.filename, "w").write(str(data))
        os.startfile(self.filename, "print")

    def reload_screen(self):
        # Change Screen
        content = self.ids.display_searched_products
        content.clear_widgets()


    def get_users_new(self):
        self.data_items = []
        mycursor.execute("SELECT buyingprice, category, code, name, sellingprice, availabilitiy, stock, id, location FROM products WHERE location =%s", (self.mylocation,))
        rows = mycursor.fetchall()
        arrows = str(mycursor.rowcount)
        self.ids.total_inventory.text = arrows + " Products"
        # create data_items
        for row in rows:
            for col in row:\
                self.data_items.append(col)


    def loadtheinitiator(self):
        self.sgday = '0'
        self.sgmonth = '0'
        self.sgyear = '0'

        self.egday = '0'
        self.egmonth = '0'
        self.egyear = '0'


    def loadspinners(self):
        # Prepare the spinners
        self.sday = self.ids.sday
        self.sday.values = [str(x) for x in range(32)]
        self.sday.bind(text=self.sssday)

        self.smonth = self.ids.smonth
        self.smonth.values = [str(x) for x in range(13)]
        self.smonth.bind(text=self.sssmonth)

        self.syear = self.ids.syear
        self.syear.values = [str(x) for x in range(2020, 2030)]
        self.syear.bind(text=self.sssyear)

        # Prepare the spinners
        self.eday = self.ids.eday
        self.eday.values = [str(x) for x in range(32)]
        self.eday.bind(text=self.eeeday)

        self.emonth = self.ids.emonth
        self.emonth.values = [str(x) for x in range(13)]
        self.emonth.bind(text=self.eeemonth)

        self.eyear = self.ids.eyear
        self.eyear.values = [str(x) for x in range(2020, 2030)]
        self.eyear.bind(text=self.eeeyear)


    def sssday(self, spinner, text):
        self.sgday = text


    def sssmonth(self, spinner, text):
        self.sgmonth = text


    def sssyear(self, spinner, text):
        self.sgyear = text


    def eeeday(self, spinner, text):
        self.egday = text


    def eeemonth(self, spinner, text):
        self.egmonth = text


    def eeeyear(self, spinner, text):
        self.egyear = text


    def periodicsearch(self):
        beginday = self.ids.sday.text
        beginmonth = self.ids.smonth.text
        beginyear = self.ids.syear.text

        endday = self.ids.eday.text
        endmonth = self.ids.emonth.text
        endyear = self.ids.eyear.text

        mindate = beginyear + "-" + beginmonth + "-" + beginday
        maxdate = endyear + "-" + endmonth + "-" + endday

        datte = {}
        datte['mindate'] = mindate
        datte['maxdate'] = maxdate

        try:
            editedmindate = datetime.datetime.strptime(mindate, '%Y-%m-%d')
            editedmaxdate = datetime.datetime.strptime(maxdate, '%Y-%m-%d')

            print(editedmaxdate, editedmindate)

            mycursor.execute("""select * from sales where date <= %s and date >= %s and location=%s""",
                             (editedmaxdate, editedmindate, self.mylocation))
            data = mycursor.fetchall()

            date = []
            amount = []
            payment = []
            served = []
            location = []
            confirmationcode = []
            customerpay = []
            balance = []

            total = str(sum(float(sale[4]) for sale in data))
            print(total)

            for sale in data:
                retrieve_date = sale[0]
                date.append(retrieve_date)

                retrieve_amount = sale[4]
                amount.append(retrieve_amount)

                retrieve_payment = sale[6]
                payment.append(retrieve_payment)

                retrieve_served = sale[7]
                served.append(retrieve_served)

                retrieve_location = sale[8]
                location.append(retrieve_location)

                retrieve_confirmationcode = sale[11]
                confirmationcode.append(retrieve_confirmationcode)

                retrieve_customerpay = sale[9]
                customerpay.append(retrieve_customerpay)

                retrieve_balance = sale[10]
                balance.append(retrieve_balance)

            _sales = dict()
            _sales['Date'] = {}
            _sales['Amount'] = {}
            _sales['Payment'] = {}
            _sales['Served'] = {}
            _sales['Location'] = {}
            _sales['Code'] = {}
            _sales['Customerpay'] = {}
            _sales['Balance'] = {}

            users_length = len(date)
            idx = 0
            while idx < users_length:
                _sales['Date'][idx] = date[idx]
                _sales['Amount'][idx] = amount[idx]
                _sales['Payment'][idx] = payment[idx]
                _sales['Served'][idx] = served[idx]
                _sales['Location'][idx] = location[idx]
                _sales['Code'][idx] = confirmationcode[idx]
                _sales['Customerpay'][idx] = customerpay[idx]
                _sales['Balance'][idx] = balance[idx]

                idx += 1

            # Change the text values
            self.ids.total_sales_select.text = "TOTAL SALES :     KES:" + " " + total
            # Change Screen
            content = self.ids.display_sales
            content.clear_widgets()
            salestable = DataTable(_sales)
            content.add_widget(salestable)

        except:
            self.showAlert("Reset your dates")

    def logout(self):
        self.parent.parent.current = 'scrn_login'


    def search_Field(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        self.crud_search_word = TextInput(hint_text='Enter Product Code or Product name')
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

        if searchCriteria == '' or searchWord == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)
        else:

            if searchCriteria == 'code':
                mycursor.execute("SELECT * FROM products WHERE location = %s and  code LIKE %s", (self.mylocation, "%" + searchWord + "%",))
            elif searchCriteria == 'name':
                mycursor.execute("SELECT * FROM products WHERE location = %s and name LIKE %s", (self.mylocation, "%" + searchWord + "%",))

        data = mycursor.fetchall()  # get the data in data variabl

        if data:
            name = [value[3] for value in data]
            code = [value[2] for value in data]
            buyingprice = [value[0] for value in data]
            sellingprice = [value[4] for value in data]
            category = [value[1] for value in data]

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

            # Change the text values
            #self.ids.total_sales.text = [sum((float(value[4]) for value in data))]

            productContents = self.ids.display_searched_products
            productstable = DataTable(_products)
            productContents.add_widget(productstable)

            self.crud_search_word.text = ''
        else:
            self.showAlert("No entries found!!")


    def view_categories(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        mycursor.execute("SELECT * FROM categorylist")
        data = mycursor.fetchall()  # get the data in data variabl
        prods = [value[0] for value in data]

        # Load the values from the database
        crud_category = Spinner(text='Select', values=prods)
        crud_submit = Button(text='View', size_hint_x=None, width=100,
                             on_release=lambda x: self.show_product_in_chosen_categories(crud_category.text))

        target.add_widget(crud_category)
        target.add_widget(crud_submit)


    def show_product_in_chosen_categories(self, crud_category):
        content = self.ids.display_categorized_products
        content.clear_widgets()
        mycursor.execute("SELECT * FROM products WHERE category=%s and location=%s", (crud_category, self.mylocation))
        data = mycursor.fetchall()  # get the data in data variabl

        if data:
            name = [value[3] for value in data]
            code = [value[2] for value in data]
            buyingprice = [value[0] for value in data]
            sellingprice = [value[4] for value in data]
            category = [value[1] for value in data]

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

        else:
            self.showAlert("No entries available")

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
            Clock.schedule_once(self.killswitch, 5)
        else:

            # ALERT DIALOG IN  PYTHON
            try:
                mycursor.execute("DELETE FROM products WHERE code=%s and location=%s", (code, self.mylocation))
                db.commit()
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

        content = self.ids.scrn_product_contents
        content.clear_widgets()
        self.crud_code.text = ''

        prodz = self.get_products()
        stocktable = DataTable(table=prodz)
        content.add_widget(stocktable)


    def update_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        crud_code = TextInput(hint_text='Product Code(Id No.)', multiline=False, write_tab=False)
        crud_name = TextInput(hint_text='Product Name + Id No', multiline=False, write_tab=False)
        crud_buyingprice = TextInput(hint_text='Buying Price', multiline=False, write_tab=False)
        crud_selling_price = TextInput(hint_text='Selling Price', multiline=False, write_tab=False)

        prods = self.db.child("MainPos").child("categorylist").get().val()
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

        self.crud_code = TextInput(hint_text='Product Code(Id No.)', multiline=False, write_tab=False)
        self.crud_name = TextInput(hint_text='Update Name', multiline=False, write_tab=False)
        self.crud_buyingprice = TextInput(hint_text='New B.price', multiline=False, write_tab=False)
        self.crud_selling_price = TextInput(hint_text='New S.Price', multiline=False, write_tab=False)

        mycursor.execute("SELECT * FROM categorylist")
        data = mycursor.fetchall()  # get the data in data variabl
        prods = [value[0] for value in data]

        # Load the values from the database
        crud_category = Spinner(text='Prod Category', values=prods)
        crud_submit = Button(text='Update', size_hint_x=None, width=100,
                             on_release=lambda x: self.update_product(self.crud_code.text, self.crud_name.text,
                                                                      self.crud_buyingprice.text,
                                                                      self.crud_selling_price.text,
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

        self.choose()

        datte = {}
        datte["code"] = code
        datte["name"] = y
        datte["buyingprice"] = buyingprice
        datte["sellingprice"] = sellingprice
        datte["category"] = category
        datte["location"] = str(self.mylocation)
        datte["image"] = self.blob_value

        if code == '' or name == '' or buyingprice == '' or sellingprice == '' or category == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)
        else:

            mycursor.execute(
                """UPDATE products SET name=%s, buyingprice=%s, sellingprice=%s, category=%s, location=%s, image=%s WHERE code =%s""",
                (y, buyingprice, sellingprice, category, str(self.mylocation), self.blob_value, code))
            db.commit()

        content = self.ids.scrn_product_contents
        content.clear_widgets()

        # Empty the widgets
        self.crud_code.text = ''
        self.crud_name.text = ''
        self.crud_buyingprice.text = ''
        self.crud_selling_price.text = ''

        users = self.get_products()
        userstable = DataTable(table=users)
        content.add_widget(userstable)


    def add_product_category_field(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        self.categoryName = TextInput(hint_text='Name of the category', multiline=False, write_tab=False)
        crud_submit = Button(text='Add Category', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_product_category(self.categoryName.text))

        target.add_widget(self.categoryName)
        target.add_widget(crud_submit)


    def add_product_category(self, categoryName):
        if categoryName == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)

        else:

            datte = {}
            datte["name"] = categoryName

            try:
                mycursor.execute("""INSERT INTO categorylist (name)  VALUES (%(name)s)""", datte)
                db.commit()

            except:
                self.showAlert("An error occured")

            else:

                mycursor.execute("SELECT * FROM categorylist")
                data = mycursor.fetchall()  # get the data in data variabl
                prods = [value[0] for value in data]

                #self.parent.parent.parent.pos_widget.thespinner = self.parent.parent.parent.pos_widget.ids.thespinners
                self.parent.parent.parent.pos_widget.thespinner.values = prods

                self.showAlert("Operation was successful")

        # content = self.ids.scrn_product_contents
        # content.clear_widgets()

        self.categoryName.text = ''

    def change_screen_alpha(self):
        self.kingusername = overall.username
        self.kinglocation = overall.location
        self.parent.parent.current = 'scrn_pos'


    def change_screen(self, instance):
        if instance.text == 'Manage Products':
            self.loadEverything()
            self.ids.scrn_mngr.current = 'scrn_product_content'

        elif instance.text == 'Manage Users':
            self.loadEverything()
            self.ids.scrn_mngr.current = 'scrn_content_manage_users'

        elif instance.text == 'Point Of Sale':
            self.loadEverything()
            self.parent.parent.current = 'scrn_pos'

        elif instance.text == 'Sales':
            self.loadEverything()
            self.ids.scrn_mngr.current = 'screen_display_sales'

        elif instance.text == 'Inventory':
            self.loadEverything()
            self.ids.scrn_mngr.current = 'screen_inventory'

        elif instance.text == 'Braches':
            self.loadEverything()
            target = self.ids.ops_fields_p
            target.clear_widgets()
            self.ids.scrn_mngr.current = 'scrn_branches'

        elif instance.text == 'StandAlone':
            self.loadEverything()
            target = self.ids.ops_fields_p
            target.clear_widgets()
            self.ids.scrn_mngr.current = 'scrn_StandAlone'

        else:
            pass


    def add_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        self.crud_code = TextInput(hint_text='Product Code(Id No.)', multiline=False, write_tab=False)
        self.crud_name = TextInput(hint_text='Product Name + Id No', multiline=False, write_tab=False)
        self.crud_buyingprice = TextInput(hint_text='Buying Price', multiline=False, write_tab=False)
        self.crud_selling_price = TextInput(hint_text='Selling Price', multiline=False, write_tab=False)

        mycursor.execute("SELECT * FROM categorylist")
        data = mycursor.fetchall()  # get the data in data variabl
        prods = [value[0] for value in data]
        # Load the values from the database
        crud_category = Spinner(text='Prod Category', values=prods)
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

        self.choose()

        datte = {}
        datte["code"] = code
        datte["name"] = y
        datte["buyingprice"] = buyingprice
        datte["sellingprice"] = sellingprice
        datte["category"] = category
        datte["location"] = str(self.mylocation)
        datte["image"] = self.blob_value

        if code == '' or name == '' or buyingprice == '' or sellingprice == '' or category == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)
        else:
            try:
                mycursor.execute(
                    """INSERT INTO products (code, name, buyingprice, sellingprice, category, location, image)  VALUES (%(code)s, %(name)s,  %(buyingprice)s,  %(sellingprice)s,%(category)s,  %(location)s, %(image)s)""",
                    datte,)
                db.commit()
            except Exception as exception:
                self.showAlert(str(exception))
                print(str(exception))
            else:
                self.showAlert("Operation was successful")

        content = self.ids.scrn_product_contents
        content.clear_widgets()

        # Empty the widgets
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


    def showAlert(self, message):
        self.notify.add_widget(Label(text='[color=#FF0000][b]' + message + '[/b][/color]', markup=True))
        self.notify.open()
        Clock.schedule_once(self.killswitch, 5)


    def remove_user(self, user):
        if user == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)
        else:

            try:
                mycursor.execute("DELETE FROM users WHERE uid=%s and location = %s", (user, self.mylocation))
                db.commit()
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

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
            Clock.schedule_once(self.killswitch, 5)

        else:

            datte = {}
            datte["name"] = name
            datte["mobile"] = mobile
            datte["uid"] = id
            datte["designation"] = designation

            try:
                mycursor.execute("""UPDATE users SET name=%s, mobile=%s, id=%s, designation=%s WHERE uid=%s and location =%s""",
                                 (name, designation, id, mobile, id, self.mylocation))
                db.commit()

            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

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
        self.mobile = TextInput(hint_text='Mobile', multiline=False, write_tab=False)
        self.idnumber = TextInput(hint_text='Id Number', multiline=False, write_tab=False)
        designation = Spinner(text='Operator', values=['Operator', 'Administrator'])

        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_user(self.bothnames.text, self.mobile.text, self.idnumber.text,
                                                                designation.text))

        target.add_widget(self.bothnames)
        target.add_widget(self.mobile)
        target.add_widget(self.idnumber)
        target.add_widget(designation)
        target.add_widget(crud_submit)


    def add_user(self, bothnames, mobile, idnumber, designation):
        datte = {}
        datte["name"] = bothnames
        datte["mobile"] = mobile
        datte["uid"] = idnumber
        datte["designation"] = designation
        datte["location"] = str(self.mylocation)

        if (bothnames == '' or mobile == '' or idnumber == '' or designation == ''):
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)
        else:

            try:
                mycursor.execute(
                    """INSERT INTO Users (name, mobile, uid, designation, location)  VALUES (%(name)s, %(mobile)s,  %(uid)s,  %(designation)s, %(location)s)""",
                    datte)
                db.commit()
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

        content = self.ids.scrn_contents
        content.clear_widgets()

        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

        self.bothnames.text = ''
        self.mobile.text = ''
        self.idnumber.text = ''


    def get_users(self):
        mycursor.execute("SELECT * FROM Users WHERE location=%s", (self.mylocation,))
        data = mycursor.fetchall()
        name = []
        mobile = []
        id = []
        designation = []

        for user in data:
            retrieve_name = user[0]
            name.append(retrieve_name)

            retrieve_mobile = user[2]
            mobile.append(retrieve_mobile)

            retrieve_id = user[3]
            id.append(retrieve_id)

            retrieve_designation = user[1]
            designation.append(retrieve_designation)

        _users = dict()
        _users['Name'] = {}
        _users['Mobile'] = {}
        _users['Id Number'] = {}
        _users['Designation'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _users['Name'][idx] = name[idx]
            _users['Mobile'][idx] = mobile[idx]
            _users['Id Number'][idx] = id[idx]
            _users['Designation'][idx] = designation[idx]

            idx += 1

        return _users





    def get_branches(self):
        mycursor.execute("SELECT * FROM braches")
        data = mycursor.fetchall()
        name = []

        if data:

            for user in data:
                retrieve_name = user[0]
                name.append(retrieve_name)

            _users = dict()
            _users['Name'] = {}

            users_length = len(name)
            idx = 0
            while idx < users_length:
                _users['Name'][idx] = name[idx]
                idx += 1

            return _users


    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()


    def get_sales(self):
        mycursor.execute("SELECT * FROM sales WHERE location=%s", (self.mylocation,))
        data = mycursor.fetchall()
        date = []
        amount = []
        payment = []
        served = []
        location = []
        confirmationcode = []
        customerpay = []
        balance = []

        self.overalldata = data

        for sale in data:
            retrieve_date = sale[0]
            date.append(retrieve_date)

            retrieve_amount = sale[4]
            amount.append(retrieve_amount)

            retrieve_payment = sale[6]
            payment.append(retrieve_payment)

            retrieve_served = sale[7]
            served.append(retrieve_served)

            retrieve_location = sale[8]
            location.append(retrieve_location)

            retrieve_confirmationcode = sale[11]
            confirmationcode.append(retrieve_confirmationcode)

            retrieve_customerpay = sale[9]
            customerpay.append(retrieve_customerpay)

            retrieve_balance = sale[10]
            balance.append(retrieve_balance)

        _sales = dict()
        _sales['Date'] = {}
        _sales['Amount'] = {}
        _sales['Payment'] = {}
        _sales['Served'] = {}
        _sales['Location'] = {}
        _sales['Code'] = {}
        _sales['Customerpay'] = {}
        _sales['Balance'] = {}

        users_length = len(date)
        idx = 0
        while idx < users_length:
            _sales['Date'][idx] = date[idx]
            _sales['Amount'][idx] = amount[idx]
            _sales['Payment'][idx] = payment[idx]
            _sales['Served'][idx] = served[idx]
            _sales['Location'][idx] = location[idx]
            _sales['Code'][idx] = confirmationcode[idx]
            _sales['Customerpay'][idx] = customerpay[idx]
            _sales['Balance'][idx] = balance[idx]

            idx += 1

        return _sales



    def get_products(self):
        mycursor.execute("SELECT * FROM products WHERE location=%s", (self.mylocation,))
        data = mycursor.fetchall()

        name = []
        code = []
        buyingprice = []
        sellingprice = []
        category = []

        for user in data:
            retrieve_name = user[3]
            name.append(retrieve_name)

            retrieve_code = user[2]
            code.append(retrieve_code)

            retrieve_buyingprice = user[0]
            buyingprice.append(retrieve_buyingprice)

            retrieve_sellingprice = user[4]
            sellingprice.append(retrieve_sellingprice)

            retrieve_category = user[1]
            category.append(retrieve_category)

        _products = dict()
        _products['Name'] = {}
        _products['Code'] = {}
        _products['Buyingprice'] = {}
        _products['Sellingprice'] = {}
        _products['Category'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _products['Name'][idx] = name[idx]
            _products['Code'][idx] = code[idx]
            _products['Buyingprice'][idx] = buyingprice[idx]
            _products['Sellingprice'][idx] = sellingprice[idx]
            _products['Category'][idx] = category[idx]

            idx += 1

        return _products


    def searchForTheDates(self):

        expensestext = self.ids.the_sales.text

        if expensestext:
            beginday = self.sgday
            beginmonth = self.sgmonth
            beginyear = self.sgyear

            endday = self.egday
            endmonth = self.egmonth
            endyear = self.egyear

            mindate = beginyear + "-" + beginmonth + "-" + beginday
            maxdate = endyear + "-" + endmonth + "-" + endday

            datte = {}
            datte['mindate'] = mindate
            datte['maxdate'] = maxdate

            mycursor.execute("""select * from sales where date >= %s and date <= %s and location=%s""", (mindate, maxdate, self.mylocation))
            data = mycursor.fetchall()

            date = []
            amount = []
            payment = []
            served = []
            location = []
            confirmationcode = []
            customerpay = []
            balance = []

            total = str(sum(float(sale[4])for sale in data))

            for sale in data:
                retrieve_date = sale[0]
                date.append(retrieve_date)

                retrieve_amount = sale[4]
                amount.append(retrieve_amount)

                retrieve_payment = sale[6]
                payment.append(retrieve_payment)

                retrieve_served = sale[7]
                served.append(retrieve_served)

                retrieve_location = sale[8]
                location.append(retrieve_location)

                retrieve_confirmationcode = sale[11]
                confirmationcode.append(retrieve_confirmationcode)

                retrieve_customerpay = sale[9]
                customerpay.append(retrieve_customerpay)

                retrieve_balance = sale[10]
                balance.append(retrieve_balance)


            _sales = dict()
            _sales['Date'] = {}
            _sales['Amount'] = {}
            _sales['Payment'] = {}
            _sales['Served'] = {}
            _sales['Location'] = {}
            _sales['Code'] = {}
            _sales['Customerpay'] = {}
            _sales['Balance'] = {}

            users_length = len(date)
            idx = 0
            while idx < users_length:
                _sales['Date'][idx] = date[idx]
                _sales['Amount'][idx] = amount[idx]
                _sales['Payment'][idx] = payment[idx]
                _sales['Served'][idx] = served[idx]
                _sales['Location'][idx] = location[idx]
                _sales['Code'][idx] = confirmationcode[idx]
                _sales['Customerpay'][idx] = customerpay[idx]
                _sales['Balance'][idx] = balance[idx]

                idx += 1

            # Change Screen
            content = self.ids.display_sales
            content.clear_widgets()
            salestable = DataTable(_sales)
            content.add_widget(salestable)

            # Try and get the total then update everything
            expensestext = self.ids.the_sales.text
            expenses = float(expensestext)
            sales = sum((float(value[4]) for value in data))

            self.ids.total_sales_select.text = "TOTAL SALES :     KES:" + " " + total

            finalmessage = 'Sales : ' + str(sales) + "\n" + 'Expenses : ' + str(expenses) + "\n"

            if (expenses == sales):
                finalmessage = finalmessage + "Profit = 0.00,   Loss = 0.00"
            elif (expenses < sales):
                finalmessage = finalmessage + "Profit: " + str(sales - expenses)
            elif (expenses > sales):
                finalmessage = finalmessage + "Loss: " + str(expenses - sales)

            # Change the text values

            self.notify.add_widget(Label(text='[color=#FF0000][b]' + str(finalmessage) + '[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 5)

            # content.clear_widgets()
            # result_thesales = self.ids.the_sales.text
            #
            # if result_thesales == '':
            #     self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            #     self.notify.open()
            #     Clock.schedule_once(self.killswitch, 3)
            # else:
            #     ref = db.reference('MainPos').child('sales')
            #     snapshot = ref.order_by_child('date').start_at(result_thesales).end_at(result_thesales + "\uf8ff").get()
            #
            #     payment = [value['payment'] for value in snapshot.values()]
            #     date = [value['date'] for value in snapshot.values()]
            #     amount = [value['amount'] for value in snapshot.values()]
            #     number = [value['number'] for value in snapshot.values()]
            #
            #     _sales = dict()
            #     _sales['payment'] = {}
            #     _sales['date'] = {}
            #     _sales['amount'] = {}
            #     _sales['number'] = {}
            #
            #     users_length = len(amount)
            #     idx = 0
            #
            #     while idx < users_length:
            #         _sales['payment'][idx] = payment[idx]
            #         _sales['date'][idx] = date[idx]
            #         _sales['amount'][idx] = amount[idx]
            #         _sales['number'][idx] = number[idx]
            #
            #         idx += 1
            #
            #     # Change Screen
            #     self.ids.scrn_mngr.current = 'screen_display_sales'
            #
            #     secondSales = self.ids.display_sales
            #     thesalesresults = DataTable(_sales)
            #     secondSales.add_widget(thesalesresults)
        else:
            self.showAlert("Enter Expenses")


class AdminApp(App):
    def build(self):
        return AdminWindow()


if __name__ == "__main__":
    active_App = AdminApp()
    active_App.run()
