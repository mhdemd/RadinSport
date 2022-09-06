from binascii import a2b_base64
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage

import PIL
from PIL import Image
import urllib.request
import urllib
import re
import requests
import webbrowser
import arabic_reshaper
from collections import  OrderedDict
from bidi.algorithm import get_display
import bidi
import csv
#import pandas as pd
#from openpyxl import load_workbook

class PopupBox(Popup):
    pop_up_text = ObjectProperty()
    def update_pop_up_text(self, p_message):
        self.pop_up_text.text = p_message

class MyBackdropBackLayer(BoxLayout):
    call = ObjectProperty(None)

class MyBackdropFrontLayer(ScreenManager):
    #transition= SwapTransition
    img = ObjectProperty(None)
    sc = ObjectProperty(None)
    
class ExampleBackdrop(Widget):
    mgr1 = ObjectProperty(None)
    mdBackdrop = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)

        global step
        global st
        global cat_list
        global product_category
        global btn_list
        global filename
        global DKPC_to_DKP_Dict

        # Initial values
        product_category = OrderedDict()
        Product_Dict = OrderedDict()
        DKPC_to_DKP_Dict = {}
        self.step = "one"
        DKP_list = []
        SellerCode = []
        Price1 = []
        Price2 = []
        Active = []
        DKPC_list = []

        # Define categories
        cat1 = get_display(arabic_reshaper.reshape("کلاه و نقاب"))
        cat2 = get_display(arabic_reshaper.reshape("قمقمه و شیکر"))
        cat3 = get_display(arabic_reshaper.reshape("طناب"))
        cat4 = get_display(arabic_reshaper.reshape("لوازم شنا"))
        cat5 = get_display(arabic_reshaper.reshape("دستکش"))
        cat6 = get_display(arabic_reshaper.reshape("بدنسازی و ایروبیک"))
        cat_list = [cat1, cat2, cat3, cat4, cat5, cat6]
        cat_dic = {"H" : cat1, "SH" : cat2, "R" : cat3, "SW" : cat4, "GL" : cat5, "PI" : cat6 }
        
        ## Get excel file from TrainBit & save it
        #url = "http://trainbit.com/files/0916917484/digikala.xlsx"
        #resp = requests.get(url)
        #urllib.request.urlretrieve(url, "digikala.xlsx")

        # Export data from excel to python dictionary
        Product_Dict = OrderedDict()

        ############# pandas
        #data = pd.read_excel (r'digikala.xlsx', sheet_name='داده ها')
        #dt ={
        #    '%s'%('کد محصول') : ['2465152', '2465152'],
        #    '%s'%('کد فروشنده') : ['H-01-01', 'H-01-02'] ,
        #    '%s'%('(ریال)قیمت فروش') : ['100000', '200000'],
        #    '%s'%('قیمت پروموشن') : ['90000', '190000'],
        #    '%s'%('فعال') : ['True', 'True'],
        #    '%s'%('کد تنوع') : ['7146411', '7146412']
        #}
        #data = pd.DataFrame(dt)

        #DKP_list = data['کد محصول'].tolist()
        #SellerCode = data["کد فروشنده"].tolist()
        #Price1 = data["(ریال)قیمت فروش"].tolist()
        #Price2 = data["قیمت پروموشن"].tolist()
        #Active = data["فعال"].tolist()
        #DKPC_list = data['کد تنوع'].tolist()

        ################## openpyxl
        #wb = load_workbook('digikala.xlsx')
        #ws = wb['داده ها']
        #c = 0
        #for i in range(2,ws.max_row+1):
        #    c += 1
        #    #print(ws.cell(row = i, column = 3).value, c)
        #    DKP_list.append(ws.cell(row = i, column = 3).value)
        #    SellerCode.append(ws.cell(row = i, column = 5).value)
        #    Price1.append(ws.cell(row = i, column = 10).value)
        #    Price2.append(ws.cell(row = i, column = 12).value)
        #    Active.append(ws.cell(row = i, column = 6).value)
        #    DKPC_list.append(ws.cell(row = i, column = 4).value)
        #print(DKP_list, "\n")


        #################### csv

        with open('digikala.csv', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                DKP_list.append(row[0])
                SellerCode.append(row[2])
                Price1.append('0')
                Price2.append('0')
                Active.append(row[3])
                DKPC_list.append(row[1])

        DKP_list = DKP_list [1:]
        SellerCode = SellerCode [1:]
        Price1 = Price1 [1:]
        Price2 = Price2 [1:]
        Active = Active [1:]
        DKPC_list = DKPC_list [1:]

        count = 0
        for  i in DKP_list:

            DKPC_to_DKP_Dict[DKPC_list[count]] = i

            Link = "https://www.digikala.com/product/" + "%s"%(i) + "/"

            #x = requests.get(Link)
            cat = cat_dic[(re.findall("^(\w+)\-", str(SellerCode[count])))[0]] if (re.findall("^(\w+)\-", str(SellerCode[count]))) != [] else  ""

            Product_Dict[i] = [str(Active[count]) ,SellerCode[count], Price1[count] ,Price2[count] ,Link, DKPC_list[count], str(cat)]

            count += 1 
        #print(DKP_to_DKPC_Dict)

        # Removing Duplicates From Dictionary
        Product = {}
        for key,value in Product_Dict.items():
            if key not in Product.keys():
                Product[key] = value
                #print(key, Product[key], "\n")


        # Filtering by active items
        self.value_product_dict = {k: v for k, v in Product.items() if v[0] == '1'}                    

    def API_get_details(self, DKP):
        
        global list_detail
        
        DKPCs = [k for k in DKPC_to_DKP_Dict if DKPC_to_DKP_Dict[k] == DKP[0]] 

        payload={}
        headers = {
            'Authorization' : 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJ0b2tlbl9pZCI6Nzc5MCwicGF5bG9hZCI6bnVsbH0.zn8Hvw5eQRNG30VShING9-l_FhiK6Gaiq73lBp6JuJZrOZjrIsya5NOZzNsKK5qa'
        }

        for i in DKPCs:
            url = "https://seller.digikala.com/api/v1/variants/%s/"%(i)

            response = requests.request("GET", url, headers=headers, data=payload)
            response_json = response.json()
            
            c = response_json['data']['stock']['selling_stock']
            
            if c != 0:
                b = response_json['data']['extra']['promotion_data']['promo_price']
                a = response_json['data']['price']['selling_price']
                break
            else:
                b = ''
                a = 'Not Stock'
                
        #print(response_json['data']['stock']['selling_stock'])
        # Title, Price1, Price2, %, stock
        list_detail = [
            response_json['data']['product']['title'],
            a,
            b,
            '%s %s'%(str(int((float(a) - float(b)) / float(a) * 100 )), '%' ) if b != "" else '',
            c,
            response_json['data']['product']['image']
                    ]

    def on_press_button(self, args):
        webbrowser.open(self.new_value_product_dict[self.button_instance[str(args)]][4])

    def callback(self, instance, return_to_cat):
        self.instance = instance
        
        if instance.text == "Weblog":
            webbrowser.open("https://radinsport.blog.ir/")

        elif instance.text == "Instagram":
            webbrowser.open("https://www.instagram.com/radin__sprt/")

        elif instance.text == "Digikala_Panel":
            webbrowser.open("https://www.digikala.com/seller/aygzu/")

        else:
            self.mgr1.current = "two screen"

            # Delete widgets
            children = self.mgr1.main.children 
            children2 = self.mgr1.main2.children 
            children3 = self.mgr1.main3.children 

            ii = 0
            while ii < len(children):
                self.mgr1.main.remove_widget(children[ii])
            ii = 0
            while ii < len(children2):           
                self.mgr1.main2.remove_widget(children2[ii])
            ii = 0
            while ii < len(children3):  
                self.mgr1.main3.remove_widget(children3[ii])

            self.step = "two"
            self.show(return_to_cat)

            if self.pop_up:
                self.pop_up.dismiss()

    def Digikala_dt(self):
        webbrowser.open(self.url)
        if self.pop_up:
            self.pop_up.dismiss()

    def collapse(self):
        if self.mgr2.collapse == True:
            self.mgr2.collapse = False
        else: 
            self.mgr2.collapse = True

    def change_screen_details(self, args):
        
        self.mgr1.sc_dt.scroll_y = 1

        # Get number of button
        j = self.button_instance[str(args)]

        # get DKP
        self.DKPC = self.new_value_product_dict[j][5]
        DKP = [k for k, v in self.filter_value_product_dict.items() if v[5] == self.DKPC]            

        # Get url
        self.url = self.new_value_product_dict[j][4]

        # API
        if self.API_get_details(DKP) == False:
            self.mgr1.current = "fifth screen"
            if self.pop_up:
                self.pop_up.dismiss()

        else:
            # Get category
            
            self.cat = self.new_value_product_dict[j][6]
            
            # Get price1 (b)
            price1 = int(list_detail[1]/10) if list_detail[1] != 'Not Stock' else 'Not Stock'
            price1 = "{:,}".format(price1) if price1 != 'Not Stock' else 'Not Stock'

            # Get price2 off (a)
            price2 = int(list_detail[2]/10) if list_detail[2] != '' else ''
            price2 = "{:,}".format(price2) if price2 != '' else ''

            # Get off
            off =  str(list_detail[3])

            # Get name
            name = list_detail[0]

            # Change current screen
            self.mgr1.current= "forth screen"
            
            # Add title
            self.mgr1.title_dt.text= "%s"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s"%(name))))
            len_title= len(name)

            if len_title < 44:
                self.mgr1.title_dt.font_size= 55
            else:
                self.mgr1.title_dt.font_size= 45

            # Add image to Carousel
            self.mgr1.image_dt.clear_widgets()

            image = AsyncImage(source= "img/%s.jpg"%(DKP[0]), size_hint=(None, None),
                size=(self.width,  self.width) )
            self.mgr1.image_dt.add_widget(image)

            #for i in range(len(list_detail) - 4):
            #    image = AsyncImage(source=list_detail[i + 4], size_hint=(None, None),
            #    size=(self.width,  self.width)
            #    )
            #    self.mgr1.image_dt.add_widget(image)

            # Add price1 label
            toman = "تومان"
            #text1 = "[size=40]%s[/size]"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s %s"%(price1, toman))))
            if price1 != 'Not Stock' and price2 != '':
                text1 = "%s"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s "%(price1 ))))  
            else:
                text1 = ''

            self.mgr1.price1_dt.text = text1

            # Add price2 label off (a)
            #text2 = "[size=55]%s[/size]"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s %s"%(price2, toman))))
            if price1 != 'Not Stock' and price2 != '':
                text2 = "%s"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s %s"%(price2, toman))))   
            elif price1 != 'Not Stock' and price2 == '':
                text2 = "%s"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s %s"%(price1, toman)))) 
            else:
                text2 = "%s"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s"%('نا موجود'))))


            self.mgr1.price2_dt.text = text2

            # Add off
            if off != "0":
                self.mgr1.off_dt.text = off
            else: 
                self.mgr1.off_dt.text = ""

            # Change return text
            self.mgr1.return_dt.text =  bidi.algorithm.get_display(arabic_reshaper.reshape("بازگشت به صفحه قبل")) 

            if self.pop_up:
                self.pop_up.dismiss()

    def show(self, cat_):
         
        # Initial values
        btn_list = []
        btn_img = []
        self.button_instance = OrderedDict()

        self.mgr1.sc.scroll_y = 1

        # Is first cat or not?
        if self.step == "one":
            cat = cat_list[1]
        elif cat_ != "":
            cat = cat_
        else:
            cat = self.instance.text

        # Filter by cat
        self.filter_value_product_dict = {k: v for k, v in self.value_product_dict.items() if v[6] == cat}                    
        self.new_value_product_dict = list(self.filter_value_product_dict.values())

        range_2 = len(self.new_value_product_dict)

        a = ""
        b = ""
        c = ""
        # Add img and price button
        for j in range(range_2):

            temp = (range_2 - ((range_2 - 1) // 3) * 3)
  
            j1 = 3 * j
            j2 = 3 * j + 1
            j3 = 3 * j + 2

            if j == (range_2 - 1) // 3:
                
                if temp == 1:
                    j2 = " "
                    j3 = " "
                elif temp == 2:
                    j3 = " "

            elif j > (range_2 - 1) // 3:
                break
                        
            # Named buttons as "btn1:btn50"
            btn_list.append("btn"+ str(j1)) 
            btn_list.append("btn"+ str(j2)) 
            btn_list.append("btn"+ str(j3))

            btn_img.append("btn"+ str(j1))
            btn_img.append("btn"+ str(j2))
            btn_img.append("btn"+ str(j3))

            ## Reshape font
            #reshaped_p3 = arabic_reshaper.reshape("تومان")
            #bidi_p3 = bidi.algorithm.get_display(reshaped_p3)
            #pr_2 = bidi_p3
#
            #reshaped_p3 = arabic_reshaper.reshape("مشاهده قیمت")
            #bidi_p3 = bidi.algorithm.get_display(reshaped_p3)
            #pr_1_1 = bidi_p3
            #pr_1_2 = bidi_p3
            #pr_1_3 = bidi_p3

            ################# img1
            pr_3_1 = list(self.filter_value_product_dict.keys())[j1]
            
            try:
                img = CoreImage("img/%s_resize_min.jpg"%(pr_3_1))
            except:
                try:
                    img = Image.open("img/%s.jpg"%(pr_3_1))
                except:
                    self.API_get_details([pr_3_1]) 
                    pic_link = list_detail[5]
                    pic_link = re.sub(',h_240,w_240', ',h_1200,w_1200', pic_link)
                    urllib.request.urlretrieve(pic_link, "img/%s.jpg"%(pr_3_1))

                img = Image.open("img/%s.jpg"%(pr_3_1))
                img.thumbnail((250, 250), PIL.Image.ANTIALIAS)
                img.save("img/%s_resize_min.jpg"%(pr_3_1), quality=80)

            btn_img[j1] = Button(background_normal="img/%s_resize_min.jpg"%(pr_3_1),  background_down= "img/%s_resize_min.jpg"%(pr_3_1),
                size_hint=(None, None),
                size=((self.width )/3, (self.width )/3)
                )
            self.mgr1.main.add_widget(btn_img[j1])
            self.button_instance[btn_img[j1].__str__()] = j1
            btn_img[j1].bind(on_press=self.show_popup)
            btn_img[j1].bind(on_release=self.change_screen_details)

            ################# img2
            if j2 != " ": 
                pr_3_2 = list(self.filter_value_product_dict.keys())[j2]

                try:
                    img = CoreImage("img/%s_resize_min.jpg"%(pr_3_2))
                except:
                    try:
                        img = Image.open("img/%s.jpg"%(pr_3_2))
                    except:
                        self.API_get_details([pr_3_2]) 
                        pic_link = list_detail[5]
                        pic_link = re.sub(',h_240,w_240', ',h_1200,w_1200', pic_link)
                        urllib.request.urlretrieve(pic_link, "img/%s.jpg"%(pr_3_2))
                        
                    img = Image.open("img/%s.jpg"%(pr_3_2))
                    img.thumbnail((250, 250), PIL.Image.ANTIALIAS)
                    img.save("img/%s_resize_min.jpg"%(pr_3_2), quality=80)

                btn_img[j2] = Button(background_normal="img/%s_resize_min.jpg"%(pr_3_2),  background_down= "img/%s_resize_min.jpg"%(pr_3_2),
                    size_hint=(None, None),
                    size=((self.width )/3, (self.width )/3)
                    )
                self.mgr1.main2.add_widget(btn_img[j2])
                self.button_instance[btn_img[j2].__str__()] = j2
                btn_img[j2].bind(on_press=self.show_popup)
                btn_img[j2].bind(on_release=self.change_screen_details)
            else:
                btn_img = Button(background_normal="img/white.jpg",  background_down= "img/white.jpg",
                    size_hint=(None, None),
                    size=((self.width )/3, (self.width )/3)
                    )
                self.mgr1.main2.add_widget(btn_img)

            ################# img3
            if j3 != " ": 
                pr_3_3 = list(self.filter_value_product_dict.keys())[j3]

                try:
                    img = CoreImage("img/%s_resize_min.jpg"%(pr_3_3))
                except:
                    try:
                        img = Image.open("img/%s.jpg"%(pr_3_3))
                    except:
                        self.API_get_details([pr_3_3]) 
                        pic_link = list_detail[5]
                        pic_link = re.sub(',h_240,w_240', ',h_1200,w_1200', pic_link)
                        urllib.request.urlretrieve(pic_link, "img/%s.jpg"%(pr_3_3))
                        
                    img = Image.open("img/%s.jpg"%(pr_3_3))
                    img.thumbnail((250, 250), PIL.Image.ANTIALIAS)
                    img.save("img/%s_resize_min.jpg"%(pr_3_3), quality=80)

                btn_img[j3] = Button(background_normal="img/%s_resize_min.jpg"%(pr_3_3),  background_down= "img/%s_resize_min.jpg"%(pr_3_3),
                    size_hint=(None, None),
                    size=((self.width )/3, (self.width )/3)
                    )
                self.mgr1.main3.add_widget(btn_img[j3])
                self.button_instance[btn_img[j3].__str__()] = j3
                btn_img[j3].bind(on_press=self.show_popup)
                btn_img[j3].bind(on_release=self.change_screen_details)

            else:
                btn_img = Button(background_normal="img/white.jpg",  background_down= "img/white.jpg",
                    size_hint=(None, None),
                    size=((self.width )/3, (self.width )/3)
                    )
            
                self.mgr1.main3.add_widget(btn_img)
            
        self.mgr2.collapse = True
    
    def show_popup(self, args):
        reshaped_loading = arabic_reshaper.reshape("لطفاً منتظر بمانید")
        bidi_loading = bidi.algorithm.get_display(reshaped_loading)
        self.pop_up = Factory.PopupBox()
        self.pop_up.update_pop_up_text(bidi_loading)
        self.pop_up.open()

class MyFloatLayout(FloatLayout):
    pass

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Radin Sport"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.primary_hue = "900"

    def build(self):
        return ExampleBackdrop()

if __name__ == "__main__":
    MainApp().run()
