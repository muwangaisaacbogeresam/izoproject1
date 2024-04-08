import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.core.window import Window
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta, datetime, date
from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from kivy_forms import MyStockFormky, MyPopup, SalesFormky, ProdctsFormky, TotalSalesFormky, ExpenseFormky, BalSheetFormky, CreditSaleForm
from my_duuka_model import MyProducts, MyStock, MySales, Expenditure, AvailiableLiquidity
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen


class SellScreen(Screen):
    def __init__(self, **kwargs):
        super(SellScreen, self).__init__(**kwargs)

        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.my_list = []
        self.hidden_list = []
        self.product = MyProducts
        self.stock = MyStock
        self.sales_form = SalesFormky()
        self.sales_form.prod_cancel_button.bind(on_press = self.delete_func)
        self.sales_form.prod_delete_item.bind(on_press = self.clear_single_item)
        self.sales_form.prod_send_button.bind(on_press = self.add_to_list)
        self.sales_form.new_customer_button.bind(on_press = self.record_sales)
        
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        main_layout.pos_hint={"top":.93}
        main_layout.add_widget(self.sales_form)
        self.add_widget(main_layout)

    def clear_single_item(self, instance):

        item_no = self.sales_form.prod_delete_item_no_input.text

        if not item_no:
            self.sales_form.message_popup('Missing Item No:', f'Fill in item number\nto be deleted eg 2')
            return
        try:
            int(item_no)
        except ValueError:
            self.sales_form.message_popup('Character error:', f'The character\nshould be a whole\nnumber')
            return
        
        item_no = int(item_no)
        self.delete_line_containing_text("Ttl", self.sales_form.my_screen_view)
        self.delete_line_containing_text("Ttl", self.sales_form.hidden_screen_view)
        
        content = self.sales_form.my_screen_view.text.splitlines() 
        content2 = self.sales_form.hidden_screen_view.text.splitlines()

        if len(content) == 0:
            self.sales_form.message_popup('Empty list:', f'There is nothing to\ndelete!!')
            self.sales_form.prod_delete_item_no_input._set_text('')
            return

        # Remove the lines corresponding to the item number
        start_index = (item_no - 1) * 5  # Each product occupies 5 lines (name, rate, quantity, cost, space)
        end_index = start_index + 5
        if 0 < item_no <= len(content) / 5:
            del content[start_index:end_index]
            del content2[start_index:end_index]

            # Update the text in the input widget
            self.sales_form.my_screen_view.text = "\n".join(content)
            self.sales_form.hidden_screen_view.text = "\n".join(content2)

            # Recalculate total cost
            self.total_cost()
            self.sales_form.prod_delete_item_no_input._set_text('')

        else:
            # message of failure to delete item
            self.sales_form.message_popup('Invalid Item No:', f'Choose the right\nproduct number')
            # Update the text in the input widget
            self.sales_form.my_screen_view.text = "\n".join(content)
            self.sales_form.hidden_screen_view.text = "\n".join(content2)
            self.total_cost()
            return
        
        
    def add_to_list(self, instance):
        unit = self.sales_form.prod_unit_input.text
        pdt_name = self.sales_form.prod_name_input.text
        qty = self.sales_form.prod_qty_input.text

        
        if not all([unit, pdt_name, qty]):
            self.sales_form.message_popup("Empty field(s)", 'please fill in missing\nfield values')
            return
        
    
        num = []
        L = 0
        alph = []
        try:
            float(qty) 
        except:
            # if string can not be converted into float we chech whether it is in fraction formate of upto 99 and 3/4
            if type(qty) != float or type(qty) != int:
                for ch in qty:
                    if ch.isdigit():
                        # print(ch)
                        num.append(float(ch))
                    elif ch == '/':
                        num.append('/')
                    elif ch.isalpha():
                        L = 0
                        alph.append(ch)
                        break

                for i, value in enumerate(num):
                    
                    if len(alph) > 0:
                        break
                    if len(num) == 4 and num[2] == '/':
                        L = 4
                        if i == 0:
                            x = value
                        elif i == 1:
                            y = value
                        elif i==3:
                            z = value
                       
                    elif len(num) == 3 and num[1] == '/':
                        L =3
                        if i == 0:
                            x = value
                        elif i == 2:
                            y = value
                    elif len(num) == 5 and num[3] == '/':
                        L=5
                        if i == 0:
                            w = value
                        elif i == 1:
                            x = value
                        elif i== 2:
                            y = value
                        elif i == 4:
                            z = value
            
                if L == 4:
                    qty = x + (y/z)
                elif L == 3:
                    qty = x/y
                elif L == 5:
                    qty = w *10 + x + (y/z)

                else:
                    self.sales_form.message_popup("Character error", 'Quantity value should\nbe number character')
                    return
        qty = abs(float(qty))
        
        if qty <= 0.0:
            self.sales_form.message_popup("Quantity value error", 'Quantity value should\nbe number greater than\nzero 0')
            return

        try:
            prod_obj = self.session.query(self.product).filter_by(product_name=pdt_name).first()
            prod_id = prod_obj.id
        except:
            self.sales_form.message_popup('Missing record', f'Product not part\nof database, pliz\ntake record of\nproduct name or\nuse select pdt\nbutton above')
            self.sales_form.prod_unit_input._set_text('')
            self.sales_form.prod_name_input._set_text('')
            self.sales_form.prod_qty_input._set_text('')
            return 
        
        stock_obj = self.session.query(self.stock).filter_by(product_id=prod_id).all()
        latest_rate = 0
        latest_stock_id = ''
        latest_prod_state = False
        latest_prod_qty = 0.0
        current_qty_value = 0.0
        
        for obj in stock_obj:
            latest_rate = obj.selling_rate
            latest_stock_id = obj.id
            latest_prod_state = obj.stock_active
            current_qty_value = obj.current_qty
            latest_prod_qty = obj.quantity
        
        self.session.close()

        prod_cost = 0.0    
        prod_cost = round(float(qty) * float(latest_rate), 1)
        
        if latest_rate == 0.0 or latest_prod_state == False: # later to be changed to current_qty_value
            print('out of stock!')
            self.sales_form.message_popup('Product Info',f'{pdt_name}\nout of stock pliz\nstock up')
            self.sales_form.clear_items()
            return
        
        same_pdt_exist, its_sumed_qty = self.check_repeated_pdts_on_list(pdt_name) # check whether same products exist on a list
        if same_pdt_exist and current_qty_value > 0.0:
            z = its_sumed_qty + float(qty)
            if z == current_qty_value:
                qty = float(qty)
            elif z < current_qty_value:
                qty = z
            else:
                self.sales_form.message_popup('Product Info',f'{pdt_name}\nhas stock quantity of\n{current_qty_value - its_sumed_qty} {unit} left you either\n restock pdt or take the\n avialable quantity')
                self.sales_form.clear_items()
                return


        if current_qty_value < float(qty) and current_qty_value > 0.0:
            self.sales_form.message_popup('Product Info',f'{pdt_name}\nhas stock quantity of\n{current_qty_value - its_sumed_qty} {unit} left you either\n restock pdt or take the\n avialable quantity')
            self.sales_form.clear_items()
            return
        
        if current_qty_value == 0.0:
            qty = float(qty)
        
        self.sales_form.my_screen_view.insert_text(f'Pdts: {pdt_name}\nQtys: {qty}\nRate: {latest_rate} per {prod_obj.unit_of_measurement}\nCost: {prod_cost}\n')
        self.sales_form.hidden_screen_view.insert_text(f'Pdts: {prod_id}\nQtys: {qty}\nRate: {latest_stock_id}\nCost: {prod_cost}\n')
        self.sales_form.clear_items()
        self.total_cost()
        # print(self.sales_form.hidden_screen_view.text)
    
    def check_repeated_pdts_on_list(self, pdt3_name):
        sum_of_qtys = 0
        same_pdt_appears = False
        my_text = self.sales_form.my_screen_view.text.splitlines()
        
        for i, text in enumerate(my_text):
            if pdt3_name in text:
                my_qty = my_text[i+1]
                my_tuple = my_qty.rpartition(': ')
                sum_of_qtys += float(my_tuple[-1])
                same_pdt_appears = True
                
        return same_pdt_appears, sum_of_qtys
      
    def total_cost(self):
        self.sales_form.cost = 0.0

        my_text = self.sales_form.my_screen_view.text.splitlines()
        my_text_hidden = self.sales_form.hidden_screen_view.text.splitlines()

        count = 0
        my_cost = False

        for hiden_text, text in zip(my_text_hidden, my_text):
            if ('Cost' in text and text[0] == 'C'):
                my_tuple = text.rpartition(' ')
                self.sales_form.cost += float(my_tuple[2])
                count += 1
                my_cost = True

        # Delete the "Ttl" line from both screen views
        self.delete_line_containing_text("Ttl", self.sales_form.my_screen_view)
        self.delete_line_containing_text("Ttl", self.sales_form.hidden_screen_view)

        if my_cost:
            ttl_cost_message = f'Ttl Cost: {self.sales_form.cost},    Item_Nos: {count}\n'
            self.sales_form.my_screen_view.insert_text('\n' + ttl_cost_message)
            self.sales_form.hidden_screen_view.insert_text('\n' + ttl_cost_message)

    def delete_line_containing_text(self, text, text_input):
        lines = text_input.text.splitlines()
        for i, line in enumerate(lines):
            if text in line:
                text_input._delete_line(i)
                break
   

    def delete_func(self, instance):
        self.sales_form.my_screen_view._set_text('')  
        self.sales_form.hidden_screen_view._set_text('') 
    
    def record_sales(self, instance):
        get_current_date = date.today()
        print(get_current_date)
        Pdt, Qtys, rate, cost, total_sale_amount = 0, 0, 0, 0, 0.0
        count = 0
        taken = False
        self.hidden_list = self.sales_form.hidden_screen_view.text
        self.hidden_list = self.hidden_list.splitlines()
      
        if len(self.hidden_list) == 0:
           self.sales_form.message_popup('Empty list', 'Please add pdts\nto your list')
           return
       
        for my_text in self.hidden_list:
            
            if 'Pdts' in my_text:
                pdt_tuple = my_text.rpartition(': ')
                Pdt = int(pdt_tuple[2])
                count += 1
            elif 'Qtys' in my_text:
                qty_tuple = my_text.rpartition(': ')
                Qtys = float(qty_tuple[2])
                count += 1
            elif 'Rate' in my_text:
                rate_tuple = my_text.rpartition(': ')
                rate = int(rate_tuple[2])
                count += 1
            elif 'Cost' in my_text and my_text[0] =='C':
                cost_tuple = my_text.rpartition(': ')
                cost = float(cost_tuple[2])
                count += 1

            if count == 4 and (rate > 0.0 and cost > 0.0 and Qtys > 0.0 and Pdt > 0):
                # print('product_name =', Pdt, 'quantity_sold =', Qtys, 'rate =', rate, 'amount =',cost)
                new_sale = MySales(product_name=Pdt, quantity_sold=Qtys, rate=rate, amount=cost)
                self.session.add(new_sale)

                # update stock objects
                update_current_stock_obj = self.session.query(MyStock).filter_by(id=rate).first()
                qty = update_current_stock_obj.current_qty - float(Qtys)
                

                if update_current_stock_obj.product_info == "current qty known":# condition to cater for stoct with declared stock qtys
                    if qty > 0.0 and update_current_stock_obj.quantity > 0.0:
                        update_current_stock_obj.current_qty = qty
                
                    elif qty == 0.0 and update_current_stock_obj.quantity > 0.0:
                        update_current_stock_obj.current_qty = 0.0 
                        update_current_stock_obj.stock_active = False

                elif update_current_stock_obj.product_info == "current qty unknown": # condition to cater for stocks without known stock qtys
                    qtys = update_current_stock_obj.quantity + float(Qtys)
                    update_current_stock_obj.quantity = qtys
                
                elif update_current_stock_obj.product_info == "cost & qty unknown":
                    qtys = update_current_stock_obj.quantity + float(Qtys)
                    update_current_stock_obj.quantity = qtys

      
                total_sale_amount += float(cost)
                taken = True
                count = 0

        self.session.commit()
        self.session.close()        
        
        self.sales_form.my_screen_view._set_text('')  
        self.sales_form.hidden_screen_view._set_text('')
        if taken:
            self.sales_form.message_popup('Successful', 'Record taken')
            self.updated_avialiable_cash(total_sale_amount, get_current_date)
           
        else: 
            self.sales_form.message_popup('Successful', 'Record taken')

    def updated_avialiable_cash(self, cash_incremt, current_date):
        first_todays_avaliable_cash = 0.0
        new_incremnt_cash = 0.0
        
        obj_avialiable_cash = self.session.query(AvailiableLiquidity).filter_by(created_date=current_date).first()
        # print(obj_avialiable_cash.created_date, date.today())
        if obj_avialiable_cash:
            new_incremnt_cash = obj_avialiable_cash.availiable_cash + cash_incremt
            obj_avialiable_cash.availiable_cash = new_incremnt_cash
            self.session.commit()
        else:
            try:
                obj = self.session.query(AvailiableLiquidity).order_by(AvailiableLiquidity.created_date.desc()).first()
                    
                first_todays_avaliable_cash += obj.availiable_cash
                new_obj = AvailiableLiquidity(availiable_cash = first_todays_avaliable_cash)
                self.session.add(new_obj)
                self.session.commit()
            except:
                print('\nfailed to register new ttl sales value')

                 
class ProductRegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.products_form = ProdctsFormky()
        self.products_form.prod_send_button.bind(on_press = self.product_register)
        self.products_form.prod_cancel_button.bind(on_press = self.clear_func)

        main_layout = BoxLayout(orientation = 'vertical', spacing=dp(10), size_hint=(1, .42))
        main_layout.pos_hint = {"top":.98}
        main_layout.add_widget(self.products_form)
        self.add_widget(main_layout)
    
    
    def checkproduct(self, product):
        prod_obj = self.session.query(MyProducts).filter_by(product_name=product).first()
        return prod_obj


    def product_register(self, instance):
        
        product_name = self.products_form.prod_name_input.text
        unit_of_measure = self.products_form.prod_measurement_unit_input.text
        print(product_name)

        if not all([product_name, unit_of_measure]):
            self.products_form.message_popup("Empty values","Missing field value(s)")
            return
        
        if self.checkproduct(product_name):
            self.products_form.message_popup("Product info","Product already exist!")
            return
        #try:
        new_prod = MyProducts(product_name=product_name, unit_of_measurement=unit_of_measure)
        self.session.add(new_prod)
        self.session.commit()
        self.products_form.message_popup("Sucess Msg",f"{product_name}\nregistered sucessfully!")
        self.products_form.registerclear()
        #except:
            #self.products_form.message_popup("Failure Msg",'failed to register')

    def clear_func(self, instance):
        self.products_form.registerclear()  
     
    
class StockingScreen(Screen):
    def __init__(self, **kwargs):
        super(StockingScreen, self).__init__(**kwargs)
        
        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.stock_form = MyStockFormky()
        self.stock_form.stock_up_button.bind(on_press = self.stocking_)
        self.stock_form.cancel_button.bind(on_press = self.cleanup)
        self.stock = MyStock
        self.product = MyProducts

        # Define button texts as attributes of MyPopup class
        
        main_layout = BoxLayout(orientation ='vertical', spacing=dp(10))
        main_layout.pos_hint={"top":.94}
        main_layout.add_widget(self.stock_form)
        self.add_widget(main_layout)

        
    def stocking_(self, instance):
        today_ = date.today()
        print(today_)
        name = self.stock_form.prod_name_input.text
        cost = self.stock_form.prod_cost_input.text
        rate = self.stock_form.prod_rate_input.text
        qty = self.stock_form.prod_qty_input.text
        pdt_stock_date = False
        pdt_is_active = False
        stock_id = ''
        current_stock = 0.0
        pdt_info = 'current qty known' #if current stock value is zero 
        latest_stock_id = 0
        
        if not all([name, cost, rate, qty]):
            self.stock_form.message_popup('Empty field(s)', 'Please enter the\nmissing field values')
            
        try:
            prod_obj = self.session.query(self.product).filter_by(product_name=name).first()
            prod_id = prod_obj.id
        except:
            self.stock_form.message_popup('Missing record', f'pdt not part\nof database, pliz\ntake record of\nproduct name')
            return 
        
        try:
            cost, rate, qty = float(cost), float(rate), float(qty)
            
        except:
            self.stock_form.message_popup('Character Error', f'Enter figures for\ncost,quantity &\nselling price')
            return

        if float(rate) == 0.0:
            self.stock_form.message_popup('Rate Value', f'Rate should be\ngreater than 0')
            return
        
        cost, rate, qty = abs(float(cost)), abs(float(rate)), abs(float(qty))

        if cost == 0.0 and qty > 0.0:
            self.stock_form.message_popup('Cost value', f'cost should be\ngreater than 0.0 if\nquantity value is greater\nthan 0.0')
            return 
        elif qty == 0.0 and cost == 0.0:
            pdt_info = 'cost & qty unknown'
        elif qty == 0.0 and cost > 0.0:
            pdt_info = "current qty unknown"
        
        # get the status of recent stock atrributes
        stock_obj = self.session.query(self.stock).filter_by(product_id=prod_id).order_by(self.stock.created_date.desc()).first()
        
        if stock_obj:

            if (stock_obj.created_date).date() == today_ and stock_obj.stock_active:
                pdt_stock_date = True
                print('today',today_)
                stock_id = stock_obj.id
                pdt_is_active = True
               
            elif (stock_obj.created_date).date() != today_ and stock_obj.stock_active:
                pdt_stock_date = False
                stock_id = stock_obj.id
                current_stock = stock_obj.current_qty
                pdt_is_active = True
                
            if stock_obj.product_info == "current qty known":

                if pdt_stock_date:

                    def callback(text):
                        print("Selected option:", text)
                    
                        if text == 'Cancel':
                            self.clear_stock()
                            self.stock_form.message_popup('No stock edit',f'No changes made to\n{name}\nstock')
                            return
                        elif text == 'Update':
                            # self.stock_form.message_popup('Stock Edit', f'You can  edit\nthe values of your\nsame date stock')
                            #stock_obj = self.session.query(self.stock).filter_by(id=stock_id).first()
                            old_pdt_cost = stock_obj.amount_bought_at
                            stock_obj.product_id = prod_id
                            stock_obj.quantity = qty
                            stock_obj.current_qty = qty
                            stock_obj.amount_bought_at = cost
                            stock_obj.selling_rate = rate
                            stock_obj.product_info = pdt_info
                            #self.session.commit()
                            self.clear_stock()
                            self.stock_form.message_popup('Sucess message', f'{name}\nedited sucessfully')
                        
                            self.update_cash_availiable(cost - old_pdt_cost)
                            return

                    # Create and open the popup, passing the callback function
                    buttons_list =  ['Update', 'Cancel']
                    informative_text = f'You seem to be\nadding the same stock\non same date\n'
                    popup = MyPopup(informative_text, buttons_list, callback=callback, title='Stock info', size_hint=(.65, .5))
                    popup.open()
        
                
                else:
                    if current_stock > 0.0 and pdt_is_active:

                        def callback(text):
                            #stock_obj2 = self.session.query(MyStock).filter_by(id=stock_id).first()
                            if text == 'stock C/f':
                            
                                carried_forward_stock_qty = stock_obj.current_qty
                                stock_obj.stock_active = False
                                stock_obj.expiry_date = 'stock C/f' # record stock current qty value as carried forward or add to new stock
                                self.session.commit()

                                new_current_qty = carried_forward_stock_qty + float(qty)
                                try:
                                    #remember to include the current_qty = qty if you update the stock module
                                    new_stock = self.stock(product_id=prod_id, quantity=qty, current_qty =new_current_qty, amount_bought_at=cost, selling_rate=rate, product_info=pdt_info)
                                    self.session.add(new_stock)
                                    self.session.commit()
                                    self.clear_stock()
                                    self.stock_form.message_popup('Sucess msg', f'{name}\nstocked sucessfully\nwith an added old qty\nof{ carried_forward_stock_qty}')
                                    self.update_cash_availiable(cost)
                                except:
                                    self.stock_form.message_popup('Failure msg',"failed to stock")
                                return
                        
                            elif text == 'damaged':
                                stock_obj.stock_active = False
                                stock_obj.damaged_pdt = True
                                stock_obj.expiry_date = 'loss' # record stock current qty value as a loss
                                self.session.commit()
                                new_stock = self.stock(product_id=prod_id, quantity=qty, current_qty =qty, amount_bought_at=cost, selling_rate=rate, product_info=pdt_info)
                                self.session.add(new_stock)
                                self.session.commit()
                                self.clear_stock()
                                self.stock_form.message_popup('Sucess msg', f'{name}\nstocked sucessfully\nat previous stock\nof {stock_obj.current_qty}')
                            
                                return
                            elif text == 'Cancel':
                                self.clear_stock()
                                self.stock_form.message_popup('No stock edit',f'No changes made to\n{name}\nstock')
                                return
                        
                        #self.stock_form.message_popup('Product Info', f'{name}\nis currently stocked\nwith quantity of {current_stock}{prod_obj.unit_of_measurement}')
                        buttons_list =  ['stock C/f', 'damaged', 'Cancel']
                        informative_text = f'{name}\nis currently stocked\nwith quantity of {current_stock}{prod_obj.unit_of_measurement}'
                        popup = MyPopup(informative_text, buttons_list, callback=callback, title='Stock info', size_hint=(.65, .5))
                        popup.open()
                    
                    else:    
                        try:
                        #remember to include the current_qty = qty if you update the stock module
                            new_stock = self.stock(product_id=prod_id, quantity=qty, current_qty =qty, amount_bought_at=cost, selling_rate=rate, product_info=pdt_info)
                            self.session.add(new_stock)
                            self.session.commit()
                            self.clear_stock()
                            self.stock_form.message_popup('Sucess msg', f'{name}\nstocked sucessfully')
                            self.update_cash_availiable(cost)
                        except:
                            self.stock_form.message_popup('Failure msg',"failed to stock")

            elif stock_obj.product_info == "current qty unknown":
                
                sales_obj = self.session.query(MySales).filter_by(rate=stock_id).all()
                sum_of_sold_pdts = sum(sale.amount for sale in sales_obj)
                profit = sum_of_sold_pdts - stock_obj.amount_bought_at

                if pdt_is_active and profit < 0: 

                    def callback(text):
                        
                            if text == 'stock C/f':
                            
                                carried_forward_stock_qty = abs(profit)
                                stock_obj.stock_active = False
                                stock_obj.amount_bought_at = sum_of_sold_pdts
                                stock_obj.expiry_date = 'stock C/f' # record stock current qty value as carried forward or add to new stock
                                self.session.commit()

                                new_current_cost = carried_forward_stock_qty + cost
                                try:
                                    #remember to include the current_qty = qty if you update the stock module
                                    new_stock = self.stock(product_id=prod_id, quantity=qty, current_qty =qty, amount_bought_at= new_current_cost, selling_rate=rate, product_info=pdt_info)
                                    self.session.add(new_stock)
                                
                                    self.clear_stock()
                                    self.stock_form.message_popup('Sucess msg', f'{name}\nstocked sucessfully\nwith an added old qty\nof{ carried_forward_stock_qty}')
                                    self.update_cash_availiable(cost)
                                except:
                                    self.stock_form.message_popup('Failure msg',"failed to stock")
                                return
                        
                            elif text == 'damaged':
                                stock_obj.stock_active = False
                                stock_obj.damaged_pdt = True
                                stock_obj.expiry_date = 'loss' # record stock current qty value as a loss
                            
                                new_stock = self.stock(product_id=prod_id, quantity=qty, current_qty =qty, amount_bought_at=cost, selling_rate=rate, product_info=pdt_info)
                                self.session.add(new_stock)
                                self.session.commit()
                                self.clear_stock()
                                self.stock_form.message_popup('Sucess msg', f'{name}\nstocked sucessfully\nat previous stock\nof {profit}')
                            
                                return
                            elif text == 'Cancel':
                                self.clear_stock()
                                self.stock_form.message_popup('No stock edit',f'No changes made to\n{name}\nstock')
                                return   
                    #self.stock_form.message_popup('Product Info', f'{name}\nis currently stocked\nwith quantity of {current_stock}{prod_obj.unit_of_measurement}')
                    buttons_list =  ['stock C/f', 'damaged', 'Cancel']
                    informative_text = f'{name}\nis currently stocked\nwith quantity of {current_stock}{prod_obj.unit_of_measurement}'
                    popup = MyPopup(informative_text, buttons_list, callback=callback, title='Stock info', size_hint=(.65, .5))
                    popup.open()
                    
                else:     
                    stock_obj.stock_active = False   
                    try:
                        #remember to include the current_qty = qty if you update the stock module
                        new_stock = self.stock(product_id=prod_id, quantity=qty, current_qty =qty, amount_bought_at=cost, selling_rate=rate, product_info=pdt_info)
                        self.session.add(new_stock)
                        self.session.commit()
                        self.clear_stock()
                        self.stock_form.message_popup('Sucess msg', f'{name}\nstocked sucessfully')
                        self.update_cash_availiable(cost)
                    except:
                        self.stock_form.message_popup('Failure msg',"failed to stock")
            
            elif stock_obj.product_info == "cost & qty unknown":
                
                
                stock_obj.stock_active = False 
                
                try:
                    #remember to include the current_qty = qty if you update the stock module
                    new_stock = self.stock(product_id=prod_id, quantity=qty, current_qty =qty, amount_bought_at=cost, selling_rate=rate, product_info=pdt_info)
                    self.session.add(new_stock)
                    self.session.commit()
                    self.clear_stock()
                    self.stock_form.message_popup('Sucess msg', f'{name}\nstocked sucessfully')
                    self.update_cash_availiable(cost)
                except:
                     self.stock_form.message_popup('Failure msg',"failed to stock")

        else:
            try:
                #remember to include the current_qty = qty if you update the stock module
                new_stock = self.stock(product_id=prod_id, quantity=qty, current_qty =qty, amount_bought_at=cost, selling_rate=rate, product_info=pdt_info)
                self.session.add(new_stock)
                self.session.commit()
                self.clear_stock()
                self.stock_form.message_popup('Sucess msg', f'{name}\nstocked sucessfully')
                self.update_cash_availiable(cost)
            except:
                self.stock_form.message_popup('Failure msg',"failed to stock")
    



    # def stocking_(self, instance):
    #     today_ = date.today()
    #     print(today_)
    #     name = self.stock_form.prod_name_input.text
    #     cost = self.stock_form.prod_cost_input.text
    #     rate = self.stock_form.prod_rate_input.text
    #     qty = self.stock_form.prod_qty_input.text
    #     pdt_info = 'current qty known'  # Default product info
    #     pdt_stock_date = False
    #     pdt_is_active = False
    #     stock_id = ''
    #     current_stock = 0.0
    #     latest_stock_id = 0
        
    #     # Validate input
    #     if not all([name, cost, rate, qty]):
    #         self.stock_form.message_popup('Empty field(s)', 'Please enter the\nmissing field values')
    #         return

    #     try:
    #         cost, rate, qty = float(cost), float(rate), float(qty)
    #     except ValueError:
    #         self.stock_form.message_popup('Character Error', 'Enter figures for\ncost, quantity &\nselling price')
    #         return

    #     if rate == 0.0:
    #         self.stock_form.message_popup('Rate Value', 'Rate should be\ngreater than 0')
    #         return

    #     cost, rate, qty = abs(cost), abs(rate), abs(qty)

    #     if cost == 0.0 and qty > 0.0:
    #         self.stock_form.message_popup('Cost value', 'Cost should be\ngreater than 0.0 if\nquantity value is greater\nthan 0.0')
    #         return 
    #     elif qty == 0.0 and cost == 0.0:
    #         pdt_info = 'cost & qty unknown'
    #     elif qty == 0.0 and cost > 0.0:
    #         pdt_info = 'current qty unknown'
        
    #     # Fetch product object
    #     prod_obj = self.session.query(self.product).filter_by(product_name=name).first()
    #     if not prod_obj:
    #         self.stock_form.message_popup('Missing record', f'Product "{name}" not found in the database')
    #         return 
        
    #     # Fetch latest stock object
    #     stock_obj = self.session.query(self.stock).filter_by(product_id=prod_obj.id).order_by(self.stock.created_date.desc()).first()

    #     if stock_obj:
    #         if stock_obj.created_date.date() == today_ and stock_obj.stock_active:
    #             pdt_stock_date = True
    #             print('today', today_)
    #             stock_id = stock_obj.id
    #             pdt_is_active = True
    #         elif stock_obj.created_date.date() != today_ and stock_obj.stock_active:
    #             pdt_stock_date = False
    #             stock_id = stock_obj.id
    #             current_stock = stock_obj.current_qty
    #             pdt_is_active = True

    #         if stock_obj.product_info == 'current qty known':
    #             # Handle stock with known quantity
    #             self.handle_known_quantity_stock()
    #         elif stock_obj.product_info == 'current qty unknown':
    #             # Handle stock with unknown quantity
    #             self.handle_unknown_quantity_stock()
    #     else:
    #         # No existing stock, create new stock
    #         self.create_new_stock()

    # def handle_known_quantity_stock(self):
    #     # Handle stock with known quantity
    #     if pdt_stock_date:
    #         def callback(text):
    #             print("Selected option:", text)
    #             if text == 'Cancel':
    #                 self.clear_stock()
    #                 self.stock_form.message_popup('No stock edit', f'No changes made to\n{name}\nstock')
    #                 return
    #             elif text == 'Update':
    #                 # Update existing stock
    #                 self.update_stock()
    #                 return

    #         # Create and open the popup for stock editing
    #         buttons_list = ['Update', 'Cancel']
    #         informative_text = f'You seem to be\nadding the same stock\non the same date\n'
    #         popup = MyPopup(informative_text, buttons_list, callback=callback, title='Stock info', size_hint=(.65, .5))
    #         popup.open()
    #     else:
    #         if current_stock > 0.0 and pdt_is_active:
    #             handle_existing_stock()
    #         else:
    #             create_new_stock()

    # def handle_unknown_quantity_stock(self):
    #     # Handle stock with unknown quantity
    #     sales_obj = self.session.query(MySales).filter_by(rate=stock_id).all()
    #     sum_of_sold_pdts = sum(sale.amount for sale in sales_obj)
    #     profit = sum_of_sold_pdts - stock_obj.amount_bought_at

    #     if pdt_is_active and profit < 0:
    #         handle_existing_stock()
    #     else:
    #         create_new_stock()

    # def handle_existing_stock(self):
    #     def callback(text):
    #         if text == 'stock C/f':
    #             # Handle stock carry forward
    #             carry_forward_stock()
    #         elif text == 'damaged':
    #             # Handle damaged stock
    #             damage_stock()
    #         elif text == 'Cancel':
    #             self.clear_stock()
    #             self.stock_form.message_popup('No stock edit', f'No changes made to\n{name}\nstock')
        
    #     buttons_list = ['stock C/f', 'damaged', 'Cancel']
    #     informative_text = f'{name}\nis currently stocked\nwith quantity of {current_stock}{prod_obj.unit_of_measurement}'
    #     popup = MyPopup(informative_text, buttons_list, callback=callback, title='Stock info', size_hint=(.65, .5))
    #     popup.open()

    # def create_new_stock(self):
    #     # Create new stock entry
    #     try:
    #         new_stock = self.stock(product_id=prod_obj.id, quantity=qty, current_qty=qty, amount_bought_at=cost, selling_rate=rate, product_info=pdt_info)
    #         self.session.add(new_stock)
    #         self.session.commit()
    #         self.clear_stock()
    #         self.stock_form.message_popup('Success msg', f'{name}\nstocked successfully')
    #         self.update_cash_available(cost)
    #     except Exception as e:
    #         print(e)
    #         self.stock_form.message_popup('Failure msg', 'Failed to stock')

    # def carry_forward_stock(self):
    #     carried_forward_stock_qty = abs(profit) if profit < 0 else 0
    #     stock_obj.stock_active = False
    #     stock_obj.amount_bought_at = sum_of_sold_pdts
    #     stock_obj.expiry_date = 'stock C/f' if profit < 0 else 'loss'
    #     self.session.commit()
    #     new_current_cost = carried_forward_stock_qty + cost
    #     try:
    #         new_stock = self.stock(product_id=prod_obj.id, quantity=qty, current_qty=qty, amount_bought_at=new_current_cost, selling_rate=rate, product_info=pdt_info)
    #         self.session.add(new_stock)
    #         self.session.commit()
    #         self.clear_stock()
    #         self.stock_form.message_popup('Success msg', f'{name}\nstocked successfully\nwith an added old qty\nof{carried_forward_stock_qty}')
    #         self.update_cash_available(cost)
    #     except Exception as e:
    #         print(e)
    #         self.stock_form.message_popup('Failure msg', 'Failed to stock')

    # def damage_stock(self):
    #     stock_obj.stock_active = False
    #     stock_obj.damaged_pdt = True
    #     stock_obj.expiry_date = 'loss'
    
    
           
            
    def clear_stock(self):
        self.stock_form.prod_name_input._set_text('')
        self.stock_form.prod_cost_input._set_text('')
        self.stock_form.prod_rate_input._set_text('')
        self.stock_form.prod_qty_input._set_text('')
    
    def cleanup(self, instance):
        self.stock_form.prod_name_input._set_text('')
        self.stock_form.prod_cost_input._set_text('')
        self.stock_form.prod_rate_input._set_text('')
        self.stock_form.prod_qty_input._set_text('')
    
    def current_qty_updated(self):
        pass

    
    def update_cash_availiable(self, cost_of_product):
        cash_to_date = 0.0
        obj_availiable_cash = self.session.query(AvailiableLiquidity).order_by(AvailiableLiquidity.created_date.desc()).first()
        if obj_availiable_cash:
            cash_to_date = obj_availiable_cash.availiable_cash - cost_of_product
            obj_availiable_cash.availiable_cash = cash_to_date
            self.session.commit()
        else:
            cash_to_date -= cost_of_product
            new_availiable_cash_obj = AvailiableLiquidity(availiable_cash = cash_to_date)
            self.session.add(new_availiable_cash_obj)
            self.session.commit()

    
   

class TotalSaleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.ttl_sale_form = TotalSalesFormky()
        self.ttl_sale_form.send_button.bind(on_press = self.total_sale)
        self.product = MyProducts
        self.ttl_sale_form.cancel_button.bind(on_press = self.clear)
        self.main_layout = BoxLayout(pos_hint={'top':.87})
        self.main_layout.add_widget(self.ttl_sale_form)
        
        self.add_widget(self.main_layout)

    def total_sale(self, instance):
        
        start_date = self.ttl_sale_form.start_date_input.text
        end_date = self.ttl_sale_form.end_date_input.text
        
        if not all([ start_date,end_date ]):
            self.ttl_sale_form.message_popup('Empty Fields', 'Pliz add values to\nmissing fields')
            return
        try:
            start_date = datetime.strptime(start_date, '%y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%y-%m-%d').date()
           
        except ValueError:
            self.ttl_sale_form.message_popup('Improper Date Format', ' Use format in the\norder yy-mm-dd\neg. 23-08-30')
            return
        
        if start_date > end_date:
            self.ttl_sale_form.message_popup('Date Info', 'start date should\nbe less than end\n date')
            return
        
        total_sales = 0.0
        sales_objects = self.session.query(MySales).all()
        date_range_valid = False # flag to indicate that the provided period has transactions that took place 

        self.ttl_sale_form.Display_screen._set_text('') # clear the Display screen Widget to get nw text
       
        rate = 0.0
        for obj in sales_objects:     
            if start_date <= (obj.created_date).date() <= end_date and obj:
                pdt = self.session.query(self.product).filter_by(id=obj.product_name).first()
                Rte = self.session.query(MyStock).filter_by(id=obj.rate).first() # get the rate at which the product was stocked
                if  Rte:  
                    rate = Rte.selling_rate

                self.ttl_sale_form.Display_screen.insert_text(f'Pdt:{pdt.product_name}\nrate: {rate}\nQty: {obj.quantity_sold}\nAmount: {obj.amount: ,}\n')
                total_sales += obj.amount # add up total cost of all products
                date_range_valid = True
        
        if date_range_valid:
            self.ttl_sale_form.total_sales_input._set_text(f'{total_sales: ,}')
        
        else:
           self.ttl_sale_form.Display_screen._set_text('') 
           self.ttl_sale_form.total_sales_input._set_text('')
           self.ttl_sale_form.message_popup('Date Info', 'The period specified\nhas no sales transaction\nrecord')
    
    def clear(self, instance):
        self.ttl_sale_form.start_date_input._set_text('') 
        self.ttl_sale_form.end_date_input._set_text('')
        self.ttl_sale_form.total_sales_input._set_text('')
        self.ttl_sale_form.Display_screen._set_text('')

class ExpenseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.expense_form = ExpenseFormky()
        self.expense_form.exp_record_button.bind(on_press= self.record_expenses)
        self.expense_form.exp_cancel_record.bind(on_press = self.clear_func)
        self.product = MyProducts
        #self.ttl_sale_form.cancel_button.bind(on_press = self.clear)
        self.main_layout = BoxLayout(pos_hint={'top':.87})
        self.main_layout.add_widget(self.expense_form)
        
        self.add_widget(self.main_layout)

    def record_expenses(self, instance):
        # self.duuka_mgt.exp_beneficary_input.setMaxLength(20)
        name = self.expense_form.exp_beneficary_input.text
        breakfast_amount = self.expense_form.exp_breakfast_input.text
        transport = self.expense_form.exp_transport_input.text
        lunch_amount = self.expense_form.exp_lunch_input.text
        wage_amount = self.expense_form.exp_wage_input.text
        salary_amount = self.expense_form.exp_salary_input.text
        rent_amount = self.expense_form.exp_rent_input.text
        # my_list = [breakfast_amount, transport, lunch_amount, wage_amount, salary_amount, rent_amount]
        Value_error = False

        if name:
            try: 
                name = float(name)
                if type(name) == float:
                    self.expense_form.message_popup('Wrong name chacters', 'Put alphabtic and numeric\nif prefered ')
                    return  
            except:
                name = name                
        else:
            self.expense_form.message_popup('Missing Beneficary', 'Put name of person or\nservice or business etc' )
            return
   
        if breakfast_amount:
                try:
                    breakfast_amount = float(breakfast_amount)
                    
                except:
                    Value_error = True
                    return
        else:
            breakfast_amount = 0.0

        if lunch_amount:
            try:
                lunch_amount = float(lunch_amount)  
            except:
                Value_error = True    
        else:
            lunch_amount = 0.0
        
        if wage_amount:
            try:
                wage_amount = float(wage_amount)   
            except:
                Value_error = True    
        else:
            wage_amount=0.0    
        
        if salary_amount:
            try:
                salary_amount = float(salary_amount) 
            except:
                Value_error = True    
        else:
            salary_amount = 0.0

        if rent_amount:
            try:
                rent_amount = float(rent_amount)    
            except:
                Value_error = True         
        else:
            rent_amount = 0.0

        if transport:
            try:
                transport = float(transport)
            except:
                Value_error = True        
        else:
            transport = 0.0
        
        if Value_error == True:
            self.expense_form.message_popup('Wrong Character', 'Except beneficary\nfill rest of fields\nwith numeric chara-\ncters.')
            return

        if lunch_amount ==0.0 and wage_amount==0.0 and rent_amount==0.0 and transport==0.0 and salary_amount==0.0 and breakfast_amount==0.0:
            self.expense_form.message_popup("Lucks Meaningful Entry", 'Fill atleast 2 valid\nvalues for record to\n be taken')
            return
        
        lunch_amount, breakfast_amount,transport, wage_amount,salary_amount, rent_amount = abs(float(lunch_amount)), abs(float(breakfast_amount)), abs(float(transport)), abs(float(wage_amount)), abs(float(salary_amount)), abs(float(rent_amount))
        new_obj = Expenditure(lunch=lunch_amount, breakfast=breakfast_amount, transport=transport, beneficary=name, wage=wage_amount, salary=salary_amount, rent=rent_amount)
        self.session.add(new_obj)
        self.session.commit()
        self.session.close()
        self.expense_form.message_popup('Sucess Message', f'{name} recorded\nsucessfully')
        my_ttl_expenses = lunch_amount + breakfast_amount + transport + wage_amount + salary_amount + rent_amount
        self.update_cash_availiable(my_ttl_expenses)
        self.expense_form.expense_clear()
    
    def clear_func(self, instance):
        self.expense_form.expense_clear()
    
    def update_cash_availiable(self, expense_cost):
        cash_to_date = 0.0
        obj_availiable_cash = self.session.query(AvailiableLiquidity).order_by(AvailiableLiquidity.created_date.desc()).first()
        if obj_availiable_cash:
            cash_to_date = obj_availiable_cash.availiable_cash - expense_cost
            obj_availiable_cash.availiable_cash = cash_to_date
            self.session.commit()
    

class BalSheetScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.balsheet_form = BalSheetFormky()
        self.balsheet_form.send_button.bind(on_press = self.balance_sheet)
        #self.balsheet_form.cancel_button.bind(on_press = self.clear)
        self.main_layout = BoxLayout(pos_hint={'top':.87})
        self.main_layout.add_widget(self.balsheet_form)
        
        self.add_widget(self.main_layout)



    def balance_sheet(self, instance):
        start_date = self.balsheet_form.start_date_input.text
        end_date = self.balsheet_form.end_date_input.text
        
        if not all([ start_date,end_date ]):
            self.balsheet_form.Display_screen._set_text('')
            self.balsheet_form.message_popup('Empty field values', 'Pliz add values to miss-\ning fields')
            return
        try:
            start_date = datetime.strptime(start_date, '%y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%y-%m-%d').date()
           
        except ValueError:
            self.balsheet_form.Display_screen._set_text('')
            self.balsheet_form.message_popup('Improper date format', ' use in the order\nyy-mm-dd (eg. 23-08-30)')
            return
        
        if start_date > end_date:
            self.balsheet_form.Display_screen._set_text('')
            self.balsheet_form.message_popup('Date Info', 'start date should be\nless than end date')
            return
        
        total_sales = 0.0
        total_stock_cost = 0.0
        current_stock_value = 0.0 
        total_loss = 0.0 
        total_expense = 0.0
        product_profits = 0.0

        expense_obj = self.session.query(Expenditure).all()
        
        self.balsheet_form.Display_screen._set_text('')
        self.balsheet_form.Display_screen.insert_text(f'Balance sheet between dates\n{start_date} and {end_date}\n')

        for obj in expense_obj:
            if start_date <= (obj.created_date).date() <= end_date and obj:  
                total_expense += (obj.lunch + obj.transport + obj.breakfast + obj.wage + obj.salary + obj.rent) 

        #Below are 3 product cases on which the statics of the business are calculated
        #1.0 Only rate is known:record only sales and contribute only to ttotal sales
        total_sale_rate_only_known = 0.0
        total_sale_rate_only_known = self.only_rate_known(start_date, end_date)        
        
        #2.0 current qty unknown
        profit_unk, loss_unk, total_sale_unk, current_stock_unk, recent_stock_unk, valid_date_unknown_qty = 0.0,0.0, 0.0,0.0, 0.0, False
        profit_unk, loss_unk, total_sale_unk, current_stock_unk, recent_stock_unk, valid_date_unknown_qty = self.pdts_with_qty_unknown(start_date, end_date)  
        #current qty known
        profit_k, loss_k, total_sale_k, current_stock_k, recent_stock_k, valid_date_known_qty =  0.0, 0.0, 0.0,0.0, 0.0, False
        profit_k, loss_k, total_sale_k, current_stock_k, recent_stock_k, valid_date_known_qty = self.pdts_with_qty_known(start_date, end_date)  
        
        #3.0 Aggregate all the three cases
        total_sales = total_sale_unk + total_sale_k + total_sale_rate_only_known
        total_stock_cost = recent_stock_k + recent_stock_unk
        product_profits = profit_unk + profit_k
        total_expense = total_expense
        total_loss = loss_k + loss_unk
        total_loss = loss_k + loss_unk
        net_profit = product_profits - total_expense - total_loss
        current_stock_value = current_stock_k + current_stock_unk
        

        if valid_date_known_qty  or valid_date_unknown_qty:
            availiable_liquidity = 0.0
            obj_availiable_cash = self.session.query(AvailiableLiquidity).order_by(AvailiableLiquidity.created_date.desc()).first()
            
            if obj_availiable_cash:
                availiable_liquidity = obj_availiable_cash.availiable_cash 
                
            self.balsheet_form.Display_screen.insert_text(f'sales: +{total_sales: ,}\nRecent stoct cost: -{total_stock_cost: ,}\nExpense: -{total_expense: ,}\nDamaged Product cost: -{total_loss}\nProduct Profits: {round(product_profits): ,}\nNet Profit: {round(net_profit):,}\nActive stock value: {round(current_stock_value, 2):,}\nAvailiable Cash: {availiable_liquidity:,}')

        else:
            self.balsheet_form.Display_screen._set_text('')
            self.balsheet_form.message_popup('Record info', f"The specified period has\nno transaction records")


    def pdts_with_qty_unknown(self, begin_date, end_date):

        profit, total_sale, valid_date_unknown_qty = self.profits_unknown_qty(begin_date, end_date)
        current_stock = self.current_stock_value_qty_unknown(begin_date, end_date)
        recent_stock = self.recent_stock_qty_unknown(begin_date, end_date)
        loss = self.loss_qty_unknown(begin_date, end_date)

        return profit, loss, total_sale, current_stock, recent_stock, valid_date_unknown_qty   

    def profits_unknown_qty(self, start_dat, end_dat):
        stock_cost_obj = self.session.query(MyStock).filter_by(product_info = "current qty unknown").all()
        sales_objects = self.session.query(MySales).all()
        total_sales = 0.0
        profit = 0.0
        valid_date = False
        
        for obj in stock_cost_obj:
            first_valid_date = None
            profit1,profit2 = 0.0, 0.0 
            triger_profit_cal = False
            sum_of_allobject_sales = 0.0
            first_all_object_date = None
            speficic_date_object_sales_sum = 0.0
            

            for sale in sales_objects:
                if obj.id == sale.rate and (sale.created_date).date() <= end_dat:
                    sum_of_allobject_sales += sale.amount
                    
                    if first_all_object_date == None:
                        first_all_object_date = (sale.created_date).date()

                if start_dat <= (sale.created_date).date()<= end_dat and obj.id == sale.rate:
                    speficic_date_object_sales_sum += sale.amount 
                    valid_date =True
            
                    if first_valid_date == None:
                        first_valid_date = (sale.created_date).date()
    
            total_sales += speficic_date_object_sales_sum 

            comparion_value = sum_of_allobject_sales - obj.amount_bought_at
            if comparion_value > 0.0 :
                triger_profit_cal = True
            
            if first_valid_date != None and first_all_object_date != None:
                
                if first_all_object_date == first_valid_date and triger_profit_cal:
                    profit1 = (sum_of_allobject_sales - obj.amount_bought_at) 
                
                elif first_valid_date > first_all_object_date and triger_profit_cal:
                    if comparion_value < speficic_date_object_sales_sum:# before we take complete addition of all values we compare with difference ttl sales and purchase price of object
                        profit2 = comparion_value
                        
                    else: 
                        profit2 = speficic_date_object_sales_sum
            
            profit += profit1 + profit2 
                               
        return profit , total_sales, valid_date

    def current_stock_value_qty_unknown(self, start_dat, end_dat):
        current_stock_value = 0.0
        stock_cost_obj = self.session.query(MyStock).filter_by(product_info = "current qty unknown", stock_active=True).all()
        for obj in stock_cost_obj:
            current_stock= 0.0
            #calculate active stock not basing on specified time but on whether the product is still active or not :
            current_stock = obj.amount_bought_at - obj.quantity * obj.selling_rate
            if current_stock >= 0.0:# record available stock value for as long as we not surpassed the cost at which the object was bought at    
                current_stock_value += current_stock

        return current_stock_value
    
    def recent_stock_qty_unknown(self, start_dat, end_dat):
        recent_stock = 0.0
        stock_cost_obj = self.session.query(MyStock).filter_by(product_info = "current qty unknown").all()
        for obj in stock_cost_obj:
            if start_dat <= (obj.created_date).date()<= end_dat:
                recent_stock += obj.amount_bought_at

        return recent_stock
     
    def loss_qty_unknown(self, start_dat, end_dat):
        stock_cost_obj = self.session.query(MyStock).filter_by(product_info = "current qty unknown", stock_active= False, expiry_date='loss').all()
        loss = 0.0
        for obj in stock_cost_obj:
            if start_dat <= (obj.updated).date()<= end_dat:
                loss += obj.amount_bought_at - obj.quantity * obj.selling_rate

        return loss
    
    def pdts_with_qty_known(self, begin_date, end_date):

        profit, total_sale, valid_date_known_qty = self.profits_known_qty(begin_date, end_date)
        current_stock = self.current_stock_value_qty_known(begin_date, end_date)
        recent_stock = self.recent_stock_qty_known(begin_date, end_date)
        loss = self.loss_qty_known(begin_date, end_date)

        return profit, loss, total_sale, current_stock, recent_stock, valid_date_known_qty   

    def profits_known_qty(self, start_dat, end_dat):
        stock_cost_obj = self.session.query(MyStock).filter_by(product_info = "current qty known").all()
        sales_objects = self.session.query(MySales).all()
        total_sales = 0.0
        profit = 0.0
        valid_date = False
        
        for obj in stock_cost_obj:
            sum_of_allobject_qtys_sold = 0.0
            speficic_date_object_sales_sum = 0.0
                
            for sale in sales_objects:
                
                if start_dat <= (sale.created_date).date()<= end_dat and obj.id == sale.rate:
                    speficic_date_object_sales_sum += sale.amount
                    sum_of_allobject_qtys_sold += sale.quantity_sold
                    valid_date =True

            if valid_date:
                total_sales += speficic_date_object_sales_sum 
                profit += (speficic_date_object_sales_sum - sum_of_allobject_qtys_sold * obj.amount_bought_at/obj.quantity)
                           
        return profit , total_sales, valid_date

    def current_stock_value_qty_known(self, start_dat, end_dat):
        current_stock_value = 0.0
        stock_cost_obj = self.session.query(MyStock).filter_by(product_info = "current qty known", stock_active=True).all()
        for obj in stock_cost_obj:
            #base calculation on whether product is still active or not but independent of specified date:
            current_stock_value += obj.current_qty * obj.amount_bought_at/obj.quantity

        return current_stock_value
    
    def recent_stock_qty_known(self, start_dat, end_dat):
        recent_stock_value = 0.0
        stock_cost_obj = self.session.query(MyStock).filter_by(product_info = "current qty known").all()
        for obj in stock_cost_obj:
            if start_dat <= (obj.created_date).date()<= end_dat:
                recent_stock_value += obj.amount_bought_at

        return recent_stock_value
     
    def loss_qty_known(self, start_dat, end_dat):
        stock_cost_obj = self.session.query(MyStock).filter_by(product_info = "current qty known", stock_active= False, expiry_date='loss').all()
        loss = 0.0
        for obj in stock_cost_obj:
            if start_dat <= (obj.updated).date()<= end_dat:
                loss += obj.current_qty * obj.amount_bought_at/obj.quantity

        return loss

    def only_rate_known(self, begin_date, end_dat):# in this case we shall only record the sales
        stock_obj = self.session.query(MyStock).filter_by(product_info="cost & qty unknown").all()
        sale_obj = self.session.query(MySales).all()
        total_sale = 0.0
        for obj in stock_obj:
            
            for _obj in sale_obj:
                if begin_date <= (obj.created_date).date() <= end_dat and _obj.rate == obj.id:
                    total_sale += _obj.amount

        return total_sale 

class CreditSaleScreen(Screen):
    def __init__(self, **kwargs):
        super(CreditSaleScreen, self).__init__(**kwargs)

        self.engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.my_list = []
        self.hidden_list = []
        self.product = MyProducts
        self.stock = MyStock
        self.sales_form = SalesFormky()
        self.sales_form.prod_cancel_button.bind(on_press = self.delete_func)
        self.sales_form.prod_delete_item.bind(on_press = self.clear_single_item)
        self.sales_form.prod_send_button.bind(on_press = self.add_to_list)
        self.sales_form.new_customer_button.bind(on_press = self.record_sales)
        
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        main_layout.pos_hint={"top":.93}
        main_layout.add_widget(self.sales_form)
        self.add_widget(main_layout)

    def clear_single_item(self, instance):

        item_no = self.sales_form.prod_delete_item_no_input.text

        if not item_no:
            self.sales_form.message_popup('Missing Item No:', f'Fill in item number\nto be deleted eg 2')
            return
        try:
            int(item_no)
        except ValueError:
            self.sales_form.message_popup('Character error:', f'The character\nshould be a whole\nnumber')
            return
        
        item_no = int(item_no)
        self.delete_line_containing_text("Ttl", self.sales_form.my_screen_view)
        self.delete_line_containing_text("Ttl", self.sales_form.hidden_screen_view)
        
        content = self.sales_form.my_screen_view.text.splitlines() 
        content2 = self.sales_form.hidden_screen_view.text.splitlines()

        if len(content) == 0:
            self.sales_form.message_popup('Empty list:', f'There is nothing to\ndelete!!')
            self.sales_form.prod_delete_item_no_input._set_text('')
            return

        # Remove the lines corresponding to the item number
        start_index = (item_no - 1) * 5  # Each product occupies 5 lines (name, rate, quantity, cost, space)
        end_index = start_index + 5
        if 0 < item_no <= len(content) / 5:
            del content[start_index:end_index]
            del content2[start_index:end_index]

            # Update the text in the input widget
            self.sales_form.my_screen_view.text = "\n".join(content)
            self.sales_form.hidden_screen_view.text = "\n".join(content2)

            # Recalculate total cost
            self.total_cost()
            self.sales_form.prod_delete_item_no_input._set_text('')

        else:
            # message of failure to delete item
            self.sales_form.message_popup('Invalid Item No:', f'Choose the right\nproduct number')
            # Update the text in the input widget
            self.sales_form.my_screen_view.text = "\n".join(content)
            self.sales_form.hidden_screen_view.text = "\n".join(content2)
            self.total_cost()
            return
        
        
    def add_to_list(self, instance):
        unit = self.sales_form.prod_unit_input.text
        pdt_name = self.sales_form.prod_name_input.text
        qty = self.sales_form.prod_qty_input.text

        
        if not all([unit, pdt_name, qty]):
            self.sales_form.message_popup("Empty field(s)", 'please fill in missing\nfield values')
            return
        
    
        num = []
        L = 0
        alph = []
        try:
            float(qty) 
        except:
            # if string can not be converted into float we chech whether it is in fraction formate of upto 99 and 3/4
            if type(qty) != float or type(qty) != int:
                for ch in qty:
                    if ch.isdigit():
                        # print(ch)
                        num.append(float(ch))
                    elif ch == '/':
                        num.append('/')
                    elif ch.isalpha():
                        L = 0
                        alph.append(ch)
                        break

                for i, value in enumerate(num):
                    
                    if len(alph) > 0:
                        break
                    if len(num) == 4 and num[2] == '/':
                        L = 4
                        if i == 0:
                            x = value
                        elif i == 1:
                            y = value
                        elif i==3:
                            z = value
                       
                    elif len(num) == 3 and num[1] == '/':
                        L =3
                        if i == 0:
                            x = value
                        elif i == 2:
                            y = value
                    elif len(num) == 5 and num[3] == '/':
                        L=5
                        if i == 0:
                            w = value
                        elif i == 1:
                            x = value
                        elif i== 2:
                            y = value
                        elif i == 4:
                            z = value
            
                if L == 4:
                    qty = x + (y/z)
                elif L == 3:
                    qty = x/y
                elif L == 5:
                    qty = w *10 + x + (y/z)

                else:
                    self.sales_form.message_popup("Character error", 'Quantity value should\nbe number character')
                    return
        qty = abs(float(qty))
        
        if qty <= 0.0:
            self.sales_form.message_popup("Quantity value error", 'Quantity value should\nbe number greater than\nzero 0')
            return

        try:
            prod_obj = self.session.query(self.product).filter_by(product_name=pdt_name).first()
            prod_id = prod_obj.id
        except:
            self.sales_form.message_popup('Missing record', f'Product not part\nof database, pliz\ntake record of\nproduct name or\nuse select pdt\nbutton above')
            self.sales_form.prod_unit_input._set_text('')
            self.sales_form.prod_name_input._set_text('')
            self.sales_form.prod_qty_input._set_text('')
            return 
        
        stock_obj = self.session.query(self.stock).filter_by(product_id=prod_id).all()
        latest_rate = 0
        latest_stock_id = ''
        latest_prod_state = False
        latest_prod_qty = 0.0
        current_qty_value = 0.0
        
        for obj in stock_obj:
            latest_rate = obj.selling_rate
            latest_stock_id = obj.id
            latest_prod_state = obj.stock_active
            current_qty_value = obj.current_qty
            latest_prod_qty = obj.quantity
        
        self.session.close()

        prod_cost = 0.0    
        prod_cost = round(float(qty) * float(latest_rate), 1)
        
        if latest_rate == 0.0 or latest_prod_state == False: # later to be changed to current_qty_value
            print('out of stock!')
            self.sales_form.message_popup('Product Info',f'{pdt_name}\nout of stock pliz\nstock up')
            self.sales_form.clear_items()
            return
        
        same_pdt_exist, its_sumed_qty = self.check_repeated_pdts_on_list(pdt_name) # check whether same products exist on a list
        if same_pdt_exist and current_qty_value > 0.0:
            z = its_sumed_qty + float(qty)
            if z == current_qty_value:
                qty = float(qty)
            elif z < current_qty_value:
                qty = z
            else:
                self.sales_form.message_popup('Product Info',f'{pdt_name}\nhas stock quantity of\n{current_qty_value - its_sumed_qty} {unit} left you either\n restock pdt or take the\n avialable quantity')
                self.sales_form.clear_items()
                return


        if current_qty_value < float(qty) and current_qty_value > 0.0:
            self.sales_form.message_popup('Product Info',f'{pdt_name}\nhas stock quantity of\n{current_qty_value - its_sumed_qty} {unit} left you either\n restock pdt or take the\n avialable quantity')
            self.sales_form.clear_items()
            return
        
        if current_qty_value == 0.0:
            qty = float(qty)
        
        self.sales_form.my_screen_view.insert_text(f'Pdts: {pdt_name}\nQtys: {qty}\nRate: {latest_rate} per {prod_obj.unit_of_measurement}\nCost: {prod_cost}\n')
        self.sales_form.hidden_screen_view.insert_text(f'Pdts: {prod_id}\nQtys: {qty}\nRate: {latest_stock_id}\nCost: {prod_cost}\n')
        self.sales_form.clear_items()
        self.total_cost()
        # print(self.sales_form.hidden_screen_view.text)
    
    def check_repeated_pdts_on_list(self, pdt3_name):
        sum_of_qtys = 0
        same_pdt_appears = False
        my_text = self.sales_form.my_screen_view.text.splitlines()
        
        for i, text in enumerate(my_text):
            if pdt3_name in text:
                my_qty = my_text[i+1]
                my_tuple = my_qty.rpartition(': ')
                sum_of_qtys += float(my_tuple[-1])
                same_pdt_appears = True
                
        return same_pdt_appears, sum_of_qtys
      
    def total_cost(self):
        self.sales_form.cost = 0.0

        my_text = self.sales_form.my_screen_view.text.splitlines()
        my_text_hidden = self.sales_form.hidden_screen_view.text.splitlines()

        count = 0
        my_cost = False

        for hiden_text, text in zip(my_text_hidden, my_text):
            if ('Cost' in text and text[0] == 'C'):
                my_tuple = text.rpartition(' ')
                self.sales_form.cost += float(my_tuple[2])
                count += 1
                my_cost = True

        # Delete the "Ttl" line from both screen views
        self.delete_line_containing_text("Ttl", self.sales_form.my_screen_view)
        self.delete_line_containing_text("Ttl", self.sales_form.hidden_screen_view)

        if my_cost:
            ttl_cost_message = f'Ttl Cost: {self.sales_form.cost},    Item_Nos: {count}\n'
            self.sales_form.my_screen_view.insert_text('\n' + ttl_cost_message)
            self.sales_form.hidden_screen_view.insert_text('\n' + ttl_cost_message)

    def delete_line_containing_text(self, text, text_input):
        lines = text_input.text.splitlines()
        for i, line in enumerate(lines):
            if text in line:
                text_input._delete_line(i)
                break
   

    def delete_func(self, instance):
        self.sales_form.my_screen_view._set_text('')  
        self.sales_form.hidden_screen_view._set_text('') 
    
    def record_sales(self, instance):
        get_current_date = date.today()
        print(get_current_date)
        Pdt, Qtys, rate, cost, total_sale_amount = 0, 0, 0, 0, 0.0
        count = 0
        taken = False
        self.hidden_list = self.sales_form.hidden_screen_view.text
        self.hidden_list = self.hidden_list.splitlines()
      
        if len(self.hidden_list) == 0:
           self.sales_form.message_popup('Empty list', 'Please add pdts\nto your list')
           return
       
        for my_text in self.hidden_list:
            
            if 'Pdts' in my_text:
                pdt_tuple = my_text.rpartition(': ')
                Pdt = int(pdt_tuple[2])
                count += 1
            elif 'Qtys' in my_text:
                qty_tuple = my_text.rpartition(': ')
                Qtys = float(qty_tuple[2])
                count += 1
            elif 'Rate' in my_text:
                rate_tuple = my_text.rpartition(': ')
                rate = int(rate_tuple[2])
                count += 1
            elif 'Cost' in my_text and my_text[0] =='C':
                cost_tuple = my_text.rpartition(': ')
                cost = float(cost_tuple[2])
                count += 1

            if count == 4 and (rate > 0.0 and cost > 0.0 and Qtys > 0.0 and Pdt > 0):
                # print('product_name =', Pdt, 'quantity_sold =', Qtys, 'rate =', rate, 'amount =',cost)
                new_sale = MySales(product_name=Pdt, quantity_sold=Qtys, rate=rate, amount=cost)
                self.session.add(new_sale)

                # update stock objects
                update_current_stock_obj = self.session.query(MyStock).filter_by(id=rate).first()
                qty = update_current_stock_obj.current_qty - float(Qtys)
                

                if update_current_stock_obj.product_info == "current qty known":# condition to cater for stoct with declared stock qtys
                    if qty > 0.0 and update_current_stock_obj.quantity > 0.0:
                        update_current_stock_obj.current_qty = qty
                
                    elif qty == 0.0 and update_current_stock_obj.quantity > 0.0:
                        update_current_stock_obj.current_qty = 0.0 
                        update_current_stock_obj.stock_active = False

                elif update_current_stock_obj.product_info == "current qty unknown": # condition to cater for stocks without known stock qtys
                    qtys = update_current_stock_obj.quantity + float(Qtys)
                    update_current_stock_obj.quantity = qtys
                
                elif update_current_stock_obj.product_info == "cost & qty unknown":
                    qtys = update_current_stock_obj.quantity + float(Qtys)
                    update_current_stock_obj.quantity = qtys

      
                total_sale_amount += float(cost)
                taken = True
                count = 0

        self.session.commit()
        self.session.close()        
        
        self.sales_form.my_screen_view._set_text('')  
        self.sales_form.hidden_screen_view._set_text('')
        if taken:
            self.sales_form.message_popup('Successful', 'Record taken')
            self.updated_avialiable_cash(total_sale_amount, get_current_date)
           
        else: 
            self.sales_form.message_popup('Successful', 'Record taken')

    def updated_avialiable_cash(self, cash_incremt, current_date):
        first_todays_avaliable_cash = 0.0
        new_incremnt_cash = 0.0
        
        obj_avialiable_cash = self.session.query(AvailiableLiquidity).filter_by(created_date=current_date).first()
        # print(obj_avialiable_cash.created_date, date.today())
        if obj_avialiable_cash:
            new_incremnt_cash = obj_avialiable_cash.availiable_cash + cash_incremt
            obj_avialiable_cash.availiable_cash = new_incremnt_cash
            self.session.commit()
        else:
            try:
                obj = self.session.query(AvailiableLiquidity).order_by(AvailiableLiquidity.created_date.desc()).first()
                    
                first_todays_avaliable_cash += obj.availiable_cash
                new_obj = AvailiableLiquidity(availiable_cash = first_todays_avaliable_cash)
                self.session.add(new_obj)
                self.session.commit()
            except:
                print('\nfailed to register new ttl sales value')
         


                 
class ManagementScreen(Screen):
    pass  # Add the content for the "Management" screen here

class WindowManager(ScreenManager):
   
    pass



class MainApp(App):
    def build(self):
        # Determine the path to the directory where main.py is located
        app_path = os.path.dirname(os.path.abspath(__file__))
        # Specify the path to your SQLite database
        db_path = os.path.join(app_path, 'Dduuka_database.db')
        # Create the SQLAlchemy engine using the path to the database
        engine = create_engine(f'sqlite:///{db_path}')
        # Your app's build logic follows...
    
        Window.size_hint = (None, None)
        Window.size = (dp(300), dp(500))
        kv = Builder.load_file("screen.kv") 
        return kv
   
if __name__ == '__main__':
    MainApp().run()
