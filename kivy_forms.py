# form.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.metrics import dp
from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from my_duuka_model import MyProducts, Expenditure, Clients  # Replace with your actual module name


class ProdctsFormky(BoxLayout):
    def __init__(self, **kwargs):
        super(ProdctsFormky, self).__init__(orientation = 'vertical', spacing = dp(10) ,**kwargs)

        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
        self.prod_name_label = Label(text='Product name(Erinya)',size_hint=(1, None), height=30)
        self.prod_name_input = TextInput(hint_text="name(erinya)",size_hint=(1, None), height=30)
        self.prod_measurement_unit_label = Label(text='Measuring unit(Ekipimo)',size_hint=(1, None), height=30)
        self.prod_measurement_unit_input = TextInput(hint_text="Selling unit",size_hint=(1, None), height=30)
        self.prod_send_button = Button(text='Register',size_hint=(1, None), height=30)
        self.prod_cancel_button = Button(text='clear',size_hint=(1, None), height=30)

        self.vert = BoxLayout(orientation = 'vertical', spacing=dp(8), size_hint=(1, .5))
        self.vert.add_widget(self.prod_name_label)
        self.vert.add_widget(self.prod_name_input)
        self.vert.add_widget(self.prod_measurement_unit_label)
        self.vert.add_widget(self.prod_measurement_unit_input)
        
        self.hori = BoxLayout(size_hint=(1, .1))
        self.hori.add_widget(self.prod_send_button)
        self.hori.add_widget(self.prod_cancel_button)

        self.add_widget(self.vert)
        self.add_widget(self.hori)

    def registerclear(self):
        self.prod_name_input._set_text('')
        self.prod_measurement_unit_input._set_text('')
          
    def message_popup(self, titl, msg):
        popup = Popup(
            title = titl,
            content = Label(text=msg), 
            size_hint = (.65, .45)
        )
        popup.open()
  


class SalesFormky(BoxLayout):
    def __init__(self, **kwargs):
        super(SalesFormky, self).__init__(orientation='vertical', spacing= dp(7), **kwargs)
        
        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
        self.prod_qty_label = Label(text='Qty', size_hint=(1, None), height=30)
        self.prod_qty_input = TextInput(hint_text="Quantity", multiline=False, background_color='white', foreground_color='black', size_hint=(1, None), height=30)
        self.prod_unit_label = Label(text='unt', size_hint=(1, None), height=30)
        self.prod_unit_input = TextInput(hint_text="Unit", multiline=False, background_color='white', foreground_color='red', size_hint=(1, None), height=30)
        self.prod_name_label = Label(text='Pdt nane',size_hint=(1, None), height=30)
        self.prod_name_input = TextInput(hint_text='Product', multiline=False, background_color='white', foreground_color='red', size_hint=(1, None), height=30)
        self.combo_button = Button(text='Select Product', size_hint=(1, None), height=30)
        
        
        self.my_screen_view = TextInput(hint_text='Display for items to be sold',background_color='white', foreground_color='black', size_hint=(1, .08), auto_indent=dp(5))
        self.hidden_screen_view = TextInput(opacity = 0, size_hint=(1, .000000001))
        self.delete_button = Button(text='Delete', size_hint=(1, None), height=40)
        # self.ttl_cost_button = Button(text='Ttl Cost', size_hint=(1, None), height=40)
        self.new_customer_button = Button(text='New Customer', size_hint=(1, None), height=30)
        self.prod_send_button = Button(text='Sell', size_hint=(1, None), height=30)
        self.prod_delete_item = Button(text='delete', size_hint=(.33, .4), pos_hint={'top':.98})
        self.prod_delete_item_no_input = TextInput(hint_text='Pdt No', size_hint=(.33, .4), pos_hint={'top':.98}, multiline=False)
        self.prod_cancel_button = Button(text='Clear all', size_hint=(.33, .4), pos_hint={'top':.98})
        
        self.drop_down = DropDown()
        
        self.combo_button.bind(on_release=self.open_drop_down)
        self.drop_down.bind(on_select=lambda instance, x:self.ret_pdt(x))
        self.select_pdt()

        self.vert_combo = BoxLayout(orientation='vertical', spacing = dp(5), size_hint=(1, .005))
        self.vert_combo.add_widget(self.combo_button)

        self.grid = GridLayout(cols=2, size_hint=(1, .028), spacing=dp(5))
        self.grid.add_widget(self.prod_name_label)
        self.grid.add_widget(self.prod_name_input)
        self.grid.add_widget(self.prod_unit_label)
        self.grid.add_widget(self.prod_unit_input)
        self.grid.add_widget(self.prod_qty_label)
        self.grid.add_widget(self.prod_qty_input)
        self.grid.add_widget(self.prod_send_button)
        self.grid.add_widget(self.new_customer_button)

        self.hori_record = BoxLayout(size_hint=(1, .02))
        self.hori_record.add_widget(self.prod_cancel_button)
        self.hori_record.add_widget(self.prod_delete_item)
        self.hori_record.add_widget(self.prod_delete_item_no_input)

        self.vert = BoxLayout(orientation='vertical',spacing=dp(5), size_hint=(1, .07))
        self.vert.add_widget(self.my_screen_view)
        self.vert.add_widget(self.hidden_screen_view)
        self.vert.add_widget(self.hori_record)
        #self.hidden_screen_view.parent = self.my_screen_view.parent
         

        self.add_widget(self.vert_combo)
        self.add_widget(self.grid)
        # self.add_widget(self.hori_cancel)
        self.add_widget(self.vert)
        
    def open_drop_down(self, button):
        max_button_width = max(button.width for button in self.drop_down.children) + 20  # Adjust for padding
        self.drop_down.width = max(max_button_width, button.width) 
        self.drop_down.open(button)
    
    def select_pdt(self):
        pdt_list  = self.get_product_names()
        for name in pdt_list:
            but = Button(text=name, size_hint=(None, None), size=(dp(200), dp(20)))
            but.bind(on_release=lambda but: self.drop_down.select(but.text))
            self.drop_down.add_widget(but)         
           
    def ret_pdt(self, pdts):  
        unit_obj = self.session.query(MyProducts).filter_by(product_name=pdts).first()
        pdt_name = pdts
        self.prod_name_input._set_text(pdt_name)
        self.prod_name_input.set_disabled(True)
        self.prod_unit_input._set_text(unit_obj.unit_of_measurement)
        self.prod_unit_input.set_disabled(True)
         
    def clear_items(self):
        self.prod_name_input._set_text('')
        self.prod_qty_input._set_text('')
        self.prod_unit_input._set_text('')    
    
    def get_product_names(self):
        items = self.session.query(MyProducts).all()
        product_names = [obj.product_name for obj in items]
        product_names.sort()
        self.session.close()
        return product_names
    
    def message_popup(self, titl, msg):
        popup = Popup(
            title = titl,
            content = Label(text=msg), 
            size_hint = (.65, .45)
        )
        popup.open()

    def clear_my_screen(self):
        self.my_screen_view._set_text("")
        self.hidden_screen_view._set_text("")


class MyPopup(Popup):
    def __init__(self, informative_text, buttons_list, callback, **kwargs):
        super(MyPopup, self).__init__(**kwargs)
        self.callback = callback
    
        self.button_texts = buttons_list
   
        self.informative_text = informative_text
        
        # Create a layout for content
        self.content_layout = BoxLayout(orientation='vertical')

        # Create a Label widget for informative text
        informative_label = Label(text=self.informative_text)

        # Create a layout for buttons
        self.buttons_layout = GridLayout(cols=2, size_hint=(1, 0.4))

        # Create buttons with desired text from attributes
        for option_text in self.button_texts:
            button = Button(text=option_text, size_hint=(.5, None), height=30)
            button.bind(on_release=self.return_text)
            self.buttons_layout.add_widget(button)

        # Add informative text and buttons layout to content layout
        self.content_layout.add_widget(informative_label)
        self.content_layout.add_widget(self.buttons_layout)

        # Set the content of the Popup
        self.content = self.content_layout

    def return_text(self, instance):
        # Call the callback function and pass the text of the pressed button
        self.callback(instance.text)
        self.dismiss()


class MyStockFormky(BoxLayout, EventDispatcher):
    
    returned_value = StringProperty()

    def __init__(self, **kwargs):
        super(MyStockFormky, self).__init__(orientation = 'vertical', spacing = dp(7), **kwargs)
        self.register_event_type('on_popup_dismiss')

    
        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.prod_qty_label = Label(text="Quantity",size_hint=(1, None), height=30)
        self.prod_qty_input = TextInput(hint_text="Quantity", multiline=False,size_hint=(1, None), height=30)
        self.prod_rate_label = Label(text="Rate",size_hint=(1, None), height=30)
        self.prod_rate_input = TextInput(hint_text="Rate",size_hint=(1, None), height=30)
        self.prod_cost_label = Label(text="Cost",size_hint=(1, None), height=30)
        self.prod_cost_input = TextInput(hint_text="Pdt stocking cost",size_hint=(1, None), height=30)
        self.prod_selling_unit_label = Label(text="Selling units",size_hint=(1, None), height=30)
        self.prod_selling_unit_input = TextInput(hint_text="selling units",size_hint=(1, None), height=30)
        self.combo_button = Button(text="Select product")
        self.prod_name_label = Label(text='Pdt nane',size_hint=(1, None), height=30)
        self.prod_name_input = TextInput(hint_text="name",size_hint=(1, None), height=30)
        self.sucess_msg_input = TextInput(hint_text="Success message")
        self.select_prod_label = Label(text='Select product below')
        #self.returned_value = None

        self.stock_up_button = Button(text='Stock Up', size_hint=(1, None), height=30)
        self.cancel_button = Button(text='Cancel', size_hint=(1, None), height=30)
        
        self.drop_down = DropDown()

        self.combo_button.bind(on_release = self.open_drop_down)
        self.drop_down.bind(on_select = lambda instance, x: self.ret_pdt(x))
        self.select_pdt()

        self.grid = GridLayout(cols = 2, size_hint=(1, .8), spacing=dp(5))
        self.grid.add_widget(self.prod_name_label)
        self.grid.add_widget(self.prod_name_input)
        self.grid.add_widget(self.prod_selling_unit_label)
        self.grid.add_widget(self.prod_selling_unit_input)
        self.grid.add_widget(self.prod_rate_label)
        self.grid.add_widget(self.prod_rate_input)
        self.grid.add_widget(self.prod_qty_label)
        self.grid.add_widget(self.prod_qty_input)
        self.grid.add_widget(self.prod_cost_label)
        self.grid.add_widget(self.prod_cost_input)
        self.grid.add_widget(self.stock_up_button)
        self.grid.add_widget(self.cancel_button)
        
        self.vert = BoxLayout(orientation='vertical', spacing = dp(5), size_hint=(1, .05))
        self.vert.add_widget(self.combo_button)
        
        self.add_widget(self.vert)
        self.add_widget(self.grid)

    def on_popup_dismiss(self,instance, selected_option ):
        
        self.returned_value = selected_option


    def open_drop_down(self, button):
        max_button_width = max(button.width for button in self.drop_down.children) + 20  # Adjust for padding
        self.drop_down.width = max(max_button_width, button.width) 
        self.drop_down.open(button)
    
    def select_pdt(self):
        pdt_list  = self.get_product_names()
        for name in pdt_list:
            but = Button(text=name, size_hint=(None, None), size=(dp(200), dp(20)))
            but.bind(on_release=lambda but: self.drop_down.select(but.text))
            self.drop_down.add_widget(but)         
           
    def ret_pdt(self, pdts):
        pdt_obj = self.session.query(MyProducts).filter_by(product_name=pdts).first()  
        pdt_name = pdts
        self.prod_name_input._set_text(pdt_name)
        self.prod_name_input.set_disabled(True)
        self.prod_selling_unit_input._set_text(pdt_obj.unit_of_measurement)
        self.prod_selling_unit_input.set_disabled(True)
       
    def clear_items(self):
        self.prod_name_input._set_text('')
        self.prod_qty_input._set_text('')
        self.prod_unit_input._set_text('')    
    
    
    def get_product_names(self):
        items = self.session.query(MyProducts).all()
        product_names = [obj.product_name for obj in items]
        product_names.sort()
        self.session.close()
        return product_names
    
    def message_popup(self, titl, msg):
        popup = Popup(
            title = titl,
            content = Label(text=msg), 
            size_hint = (.65, .45)
        )
        popup.open()
    
   


class TotalSalesFormky(BoxLayout):
    def __init__(self,  **kwargs):
        super(TotalSalesFormky, self).__init__(orientation ='vertical', spacing = dp(5),**kwargs)

        self.start_date_label = Label(text='start date:', size_hint=(.5, None), height=30)
        self.start_date_input = TextInput(hint_text='year-month-date', multiline = False, size_hint=(.5, None), height=30)
        self.end_date_label = Label(text='end date:', size_hint=(.5, None), height=30)
        self.end_date_input = TextInput(hint_text='year-month-date', multiline = False, size_hint=(.5, None), height=30)
        self.send_button = Button(text='send', size_hint=(.5, None), height=30)
        self.cancel_button = Button(text='cancel', size_hint=(.5, None), height=30)
        self.total_sales_label = Label(text='Ttl sales:', size_hint=(.5, None), height=30)
        self.total_sales_input = TextInput(multiline = False, size_hint=(.5, None), height=30)
        self.Display_screen = TextInput(background_color = 'white', foreground_color = 'black', size_hint=(1, .81))
        self.my_space_lebal = Label(size_hint=(1, .19))

        self.grid = GridLayout(cols = 2, size_hint = (1, .28), spacing = dp(5))
        self.grid.add_widget(self.start_date_label)
        self.grid.add_widget(self.start_date_input)
        self.grid.add_widget(self.end_date_label)
        self.grid.add_widget(self.end_date_input)
        self.grid.add_widget(self.send_button)
        self.grid.add_widget(self.cancel_button)
        self.grid.add_widget(self.total_sales_label)
        self.grid.add_widget(self.total_sales_input)

        self.vet = BoxLayout(orientation="vertical", size_hint = (1, .7))
        self.vet.add_widget(self.Display_screen)
        self.vet.add_widget(self.my_space_lebal)

        self.add_widget(self.grid)
        self.add_widget(self.vet)        

    def message_popup(self, titl, msg):
        popup = Popup(
            title = titl,
            content = Label(text=msg), 
            size_hint = (.65, .45)
        )
        popup.open()

class ClientRegistrationForm(BoxLayout):
    def __init__(self, **kwargs):
        super(ClientRegistrationForm, self).__init__(**kwargs)
        self.client_name_label = Label(text = "Name:")
        self.client_name_input = TextInput(text_hint = "Isaac", multiline = False)
        self.phone_no_label = Label(text="Phone:")
        self.phone_no_input = TextInput(text_hint = "0782037811", multiline = False)



        
class ExpenseFormky(BoxLayout):
    def __init__(self,  **kwargs):
        super(ExpenseFormky, self).__init__(orientation ='vertical', spacing = dp(5),**kwargs)

        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.exp_lunch_label = Label(text='Lunch amount:',size_hint=(.5, None), height=30)
        self.exp_lunch_input = TextInput(size_hint=(.5, None), height=30, multiline=False)
        self.exp_breakfast_label = Label(text='berakfast amount',size_hint=(.5, None), height=30)
        self.exp_breakfast_input = TextInput(size_hint=(.5, None), height=30, multiline=False)
        self.exp_transport_label = Label(text='Transport amount',size_hint=(.5, None), height=30)
        self.exp_transport_input = TextInput(size_hint=(.5, None), height=30, multiline=False)
        self.exp_beneficary_button = Button(text='Benficary name',size_hint=(.5, None), height=30)
        self.exp_beneficary_input = TextInput(size_hint=(.5, None), height=30, multiline=False)
        self.exp_wage_label = Label(text='wage amount',size_hint=(.5, None), height=30)
        self.exp_wage_input = TextInput(size_hint=(.5, None), height=30, multiline=False)
        self.exp_salary_label = Label(text='Salary amount',size_hint=(.5, None), height=30)
        self.exp_salary_input = TextInput(size_hint=(.5, None), height=30, multiline=False)
        self.exp_rent_label = Label(text='Rent amount',size_hint=(.5, None), height=30)
        self.exp_rent_input = TextInput(size_hint=(.5, None), height=30, multiline=False)
        
        self.service_type_label = Label(text='service type:',size_hint=(.5, None), height=30)
        self.service_type_input = TextInput(size_hint=(.5, None), height=30, multiline=False)
        self.service_rendered_amount_label = Label(text ='Service amount:',size_hint=(.5, None), height=30)
        self.service_rendered_amount_input = TextInput(size_hint=(.5, None), height=30, multiline=False)
        
        self.exp_other_button = Button(text='other expense',size_hint=(.5, None), height=30)
        self.exp_record_button = Button(text='Record',size_hint=(.5, None), height=30)
        self.exp_cancel_record = Button(text = 'cancel',size_hint=(.5, None), height=30)

        self.drop_down = DropDown()
        
        self.exp_beneficary_button.bind(on_release = self.open_drop_down)
        self.drop_down.bind(on_select = lambda instance, x: self.ret_beneficary(x))
        self.select_beneficary()

        self.grid_buttons = GridLayout(cols=2, size_hint=(1, .8), spacing=dp(6))
        self.grid_buttons.add_widget(self.exp_beneficary_button)
        self.grid_buttons.add_widget(self.exp_beneficary_input)
        self.grid_buttons.add_widget(self.exp_breakfast_label)
        self.grid_buttons.add_widget(self.exp_breakfast_input)
        self.grid_buttons.add_widget(self.exp_lunch_label)
        self.grid_buttons.add_widget(self.exp_lunch_input)
        self.grid_buttons.add_widget(self.exp_transport_label)
        self.grid_buttons.add_widget(self.exp_transport_input)
        self.grid_buttons.add_widget(self.exp_wage_label)
        self.grid_buttons.add_widget(self.exp_wage_input)
        self.grid_buttons.add_widget(self.exp_salary_label)
        self.grid_buttons.add_widget(self.exp_salary_input)
        self.grid_buttons.add_widget(self.exp_rent_label)
        self.grid_buttons.add_widget(self.exp_rent_input)
        self.grid_buttons.add_widget(self.exp_record_button)
        self.grid_buttons.add_widget(self.exp_cancel_record)
        # self.grid_buttons.addWidget(self.exp_other_button)
        self.add_widget(self.grid_buttons)

    def open_drop_down(self, button):
        max_button_width = max(button.width for button in self.drop_down.children) + 20  # Adjust for padding
        self.drop_down.width = max(max_button_width, button.width) 
        self.drop_down.open(button)
    
    def select_beneficary(self):
        pdt_list  = self.get_beneficary_names()
        for name in pdt_list:
            but = Button(text=name, size_hint=(None, None), size=(dp(200), dp(20)))
            but.bind(on_release=lambda but: self.drop_down.select(but.text))
            self.drop_down.add_widget(but)         
           
    def ret_beneficary(self, pdts): 
        pdt_name = pdts
        self.exp_beneficary_input._set_text(pdt_name)
         
    def get_beneficary_names(self):
        items = self.session.query(Expenditure).all()
        product_names = [obj.beneficary for obj in items]
        product_names.sort()
        self.session.close()
        return product_names
    
    def message_popup(self, titl, msg):
        popup = Popup(
            title = titl,
            content = Label(text=msg), 
            size_hint = (.65, .45)
        )
        popup.open()
    
    def expense_clear(self):
        self.exp_beneficary_input._set_text('')
        self.exp_breakfast_input._set_text('')
        self.exp_transport_input._set_text('')
        self.exp_lunch_input._set_text('')
        self.exp_wage_input._set_text('')
        self.exp_salary_input._set_text('')
        self.exp_rent_input._set_text('')

         
class BalSheetFormky(BoxLayout):
    def __init__(self, **kwargs):
        super(BalSheetFormky, self).__init__(orientation ='vertical', spacing = dp(5), **kwargs)

        self.start_date_label = Label(text='start date:', size_hint=(.5, None), height=30)
        self.start_date_input = TextInput(hint_text='year-month-date', multiline = False, size_hint=(.5, None), height=30)
        self.end_date_label = Label(text='end date:', size_hint=(.5, None), height=30)
        self.end_date_input = TextInput(hint_text='year-month-date', multiline = False, size_hint=(.5, None), height=30)
        self.send_button = Button(text='send', size_hint=(.5, None), height=30)
        self.cancel_button = Button(text='cancel', size_hint=(.5, None), height=30)
        self.Display_screen = TextInput(background_color = 'white', foreground_color = 'black', size_hint=(1, .81))
        self.my_space_lebal = Label(size_hint=(1, .19))

        self.grid = GridLayout(cols = 2, size_hint = (1, .2), spacing = dp(5))
        self.grid.add_widget(self.start_date_label)
        self.grid.add_widget(self.start_date_input)
        self.grid.add_widget(self.end_date_label)
        self.grid.add_widget(self.end_date_input)
        self.grid.add_widget(self.send_button)
        self.grid.add_widget(self.cancel_button)

        self.vet = BoxLayout(orientation="vertical", size_hint = (1, .8))
        self.vet.add_widget(self.Display_screen)
        self.vet.add_widget(self.my_space_lebal)

        self.add_widget(self.grid)
        self.add_widget(self.vet)        

    def message_popup(self, titl, msg):
        popup = Popup(
            title = titl,
            content = Label(text=msg), 
            size_hint = (.65, .45)
        )
        popup.open()
        

class CreditSaleForm(BoxLayout):
    def __init__(self, **kwargs):
        super(CreditSaleForm, self).__init__(orientation='vertical', spacing = dp(5),**kwargs)
        
        self.pay_date_label = Label(text='Pay date')
        self.pay_date = TextInput(text_hint='year-month-date', multiline=False)
        self.select_items = Button(text='select items')
        self.item_name_label = Label(text='Product name')
        self.item_name_input = TextInput(text_hint='Pdt name', multiline=False)
        self.unit_of_measure_label = Label(text='unit')
        self.unit_of_measure_input = TextInput(multiline=False)
        self.quantity_label = Label(text='Quantity')
        self.quantity_input = TextInput(multiline=False)
        self.add_item_button = Button(text='Add')
        self.list_of_items_to_be_taken = TextInput(text_hint='Add items here')

        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
        self.client_combo_button = Button(text='Select Phone No', size_hint=(1, None), height=30)
        self.creditor_name_label = Label(text='Creditor Name')
        self.creditor_name = TextInput(text_hint='Isaac', multiline=False)
        self.creditor_tele_label = Label(text='Phone Number')
        self.creditor_tele = TextInput(text_hint='0782037811', multiline=False)
        self.pay_date_label = Label('Pay date')
        self.pay_date = TextInput(text_hint='year-month-date', multiline=False)
        self.prod_qty_label = Label(text='Qty', size_hint=(1, None), height=30)
        self.prod_qty_input = TextInput(hint_text="Quantity", multiline=False, background_color='white', foreground_color='black', size_hint=(1, None), height=30)
        self.prod_unit_label = Label(text='unt', size_hint=(1, None), height=30)
        self.prod_unit_input = TextInput(hint_text="Unit", multiline=False, background_color='white', foreground_color='red', size_hint=(1, None), height=30)
        self.prod_name_label = Label(text='Pdt nane',size_hint=(1, None), height=30)
        self.prod_name_input = TextInput(hint_text='Product', multiline=False, background_color='white', foreground_color='red', size_hint=(1, None), height=30)
        self.combo_button = Button(text='Select Product', size_hint=(1, None), height=30)
        
        self.my_screen_view = TextInput(hint_text='Display for items to be sold',background_color='white', foreground_color='black', size_hint=(1, .08), auto_indent=dp(5))
        self.hidden_screen_view = TextInput(opacity = 0, size_hint=(1, .000000001))
        self.delete_button = Button(text='Delete', size_hint=(1, None), height=40)
        # self.ttl_cost_button = Button(text='Ttl Cost', size_hint=(1, None), height=40)
        self.new_customer_button = Button(text='New Customer', size_hint=(1, None), height=30)
        self.prod_send_button = Button(text='Sell', size_hint=(1, None), height=30)
        self.prod_delete_item = Button(text='delete', size_hint=(.33, .4), pos_hint={'top':.98})
        self.prod_delete_item_no_input = TextInput(hint_text='Pdt No', size_hint=(.33, .4), pos_hint={'top':.98}, multiline=False)
        self.prod_cancel_button = Button(text='Clear all', size_hint=(.33, .4), pos_hint={'top':.98})
        
        self.drop_down = DropDown()
        
        self.combo_button.bind(on_release=self.open_drop_down)
        self.drop_down.bind(on_select=lambda instance, x:self.ret_pdt(x))
        self.select_pdt()

        self.client_name_drop_down = DropDown()
        self.client_combo_button.bind(on_release=self.open_client_name_drop_down)
        self.client_name_drop_down.bind(on_select = lambda instance, y:self.ret_name(y))
        self.select_name()

        #consider client widget
        self.client_gird = GridLayout(cols=2, size_hint = (1, 0.012), spacing=dp(5))
        self.client_gird.add_widget(self.creditor_name_label)
        self.client_gird.add_widget(self.creditor_name) 
        self.client_gird.add_widget(self.creditor_tele_label)
        self.client_gird.add_widget(self.creditor_tele)
        self.client_gird.add_widget(self.pay_date_label)
        self.client_gird.add_widget(self.pay_date)

        self.client_layout = BoxLayout(orientation = "vertical")
        self.client_layout.add_widget(self.client_combo_button)
        self.client_layout.add_widget(self.client_gird) 

        #consider product widgets
        self.vert_combo = BoxLayout(orientation='vertical', spacing = dp(5), size_hint=(1, .005))
        self.vert_combo.add_widget(self.combo_button)

        self.grid = GridLayout(cols=2, size_hint=(1, .028), spacing=dp(5))
        self.grid.add_widget(self.prod_name_label)
        self.grid.add_widget(self.prod_name_input)
        self.grid.add_widget(self.prod_unit_label)
        self.grid.add_widget(self.prod_unit_input)
        self.grid.add_widget(self.prod_qty_label)
        self.grid.add_widget(self.prod_qty_input)
        self.grid.add_widget(self.prod_send_button)
        self.grid.add_widget(self.new_customer_button)

        self.hori_record = BoxLayout(size_hint=(1, .02))
        self.hori_record.add_widget(self.prod_cancel_button)
        self.hori_record.add_widget(self.prod_delete_item)
        self.hori_record.add_widget(self.prod_delete_item_no_input)

        self.vert = BoxLayout(orientation='vertical',spacing=dp(5), size_hint=(1, .07))
        self.vert.add_widget(self.my_screen_view)
        self.vert.add_widget(self.hidden_screen_view)
        self.vert.add_widget(self.hori_record)
        #self.hidden_screen_view.parent = self.my_screen_view.parent
         
        self.pdt_vert_layout = BoxLayout(orientation = "vertical")
        self.pdt_vert_layout.add_widget(self.vert_combo)
        self.pdt_vert_layout.add_widget(self.grid)
        self.pdt_vert_layout.add_widget(self.vert)
        # self.add_widget(self.hori_cancel)
        self.add_widget(self.client_layout)
        self.add_widget(self.pdt_vert_layout)
        
    def open_drop_down(self, button):
        max_button_width = max(button.width for button in self.drop_down.children) + 20  # Adjust for padding
        self.drop_down.width = max(max_button_width, button.width) 
        self.drop_down.open(button)
    
    def select_pdt(self):
        pdt_list  = self.get_product_names()
        for name in pdt_list:
            but = Button(text=name, size_hint=(None, None), size=(dp(200), dp(20)))
            but.bind(on_release=lambda but: self.drop_down.select(but.text))
            self.drop_down.add_widget(but)         
           
    def ret_pdt(self, pdts):  
        unit_obj = self.session.query(MyProducts).filter_by(product_name=pdts).first()
        pdt_name = pdts
        self.prod_name_input._set_text(pdt_name)
        self.prod_name_input.set_disabled(True)
        self.prod_unit_input._set_text(unit_obj.unit_of_measurement)
        self.prod_unit_input.set_disabled(True)
         
    def clear_items(self):
        self.prod_name_input._set_text('')
        self.prod_qty_input._set_text('')
        self.prod_unit_input._set_text('')    
    
    def get_product_names(self):
        items = self.session.query(MyProducts).all()
        product_names = [obj.product_name for obj in items]
        product_names.sort()
        self.session.close()
        return product_names
    
    def message_popup(self, titl, msg):
        popup = Popup(
            title = titl,
            content = Label(text=msg), 
            size_hint = (.65, .45)
        )
        popup.open()

    def clear_my_screen(self):
        self.my_screen_view._set_text("")
        self.hidden_screen_vi
    
    #client detail functions
    def open_client_drop_down(self, button):
        max_button_width = max(button.width for button in self.cliet_name_drop_down.children) + 20  # Adjust for padding
        self.client_name_drop_down.width = max(max_button_width, button.width) 
        self.client_name_drop_down.open(button)
    
    def select_client_phone(self):
        client_phone_list  = self.get_client_phone()
        for phone in client_phone_list:
            but = Button(text=phone, size_hint=(None, None), size=(dp(200), dp(20)))
            but.bind(on_release=lambda but: self.client_name_drop_down.select(but.text))
            self.client_name_drop_down.add_widget(but)   
    
           
    def ret_name(self, phone):  
        obj = self.session.query(Clients).filter_by(tele_no=phone).first()
        self.creditor_name._set_text(obj.name)
        self.creditor_tele._set_text(obj.tele_no)

    def get_client_phone(self):
        items = self.session.query(Clients).all()
        phone = [obj.tele_no for obj in items] 
        self.session.close()
        return phone