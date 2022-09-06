from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.graphics import BorderImage
from kivymd.uix import button
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.button import MDRoundFlatIconButton
from kivy.core.image import Image as CoreImage
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

import urllib.request
import re
import requests
import webbrowser
import convert_numbers
import arabic_reshaper
from bs4 import BeautifulSoup
from collections import _OrderedDictItemsView, OrderedDict
from bidi.algorithm import get_display
import bidi
import csv 
from datetime import date
import os

#Window.size = (900, 1080)

class MyLayout(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global cat_list
        global product_category
        global btn_list
        global filename
        global bidi_p3
        global key_product_dict
        global value_product_dict


        # Initial values
        key_product_dict = []
        value_product_dict = []
        product_category = OrderedDict()

        # Reshape font
        reshaped_p3 = arabic_reshaper.reshape("تومان")
        bidi_p3 = bidi.algorithm.get_display(reshaped_p3)

        # name of csv file 
        today = date.today()
        date_today = today.strftime("%b-%d-%Y")
        filename = "%s.csv"%(date_today)

        # Define categories
        cat1 = get_display(arabic_reshaper.reshape("کلاه"))
        cat2 = get_display(arabic_reshaper.reshape("قمقمه و شیکر"))
        cat3 = get_display(arabic_reshaper.reshape("دستکش و لوازم بدنسازی"))
        cat4 = get_display(arabic_reshaper.reshape("حوله و مایو"))
        cat_list = [cat1, cat2, cat3, cat4]

        # Define Category link
        product_category[str(cat1)] = "https://www.digikala.com/seller/aygzu/?category[0]=9539&category[1]=9938&pageno=1&sortby=4"
        product_category[str(cat2)] = "https://www.digikala.com/seller/aygzu/?category[0]=6102&pageno=1&last_filter=category&last_value=6102&sortby=4"
        product_category[str(cat3)] = "https://www.digikala.com/seller/aygzu/?category[0]=6116&category[1]=9524&category[2]=6432&category[3]=9428&category[4]=9551&pageno=1&last_filter=category&last_value=6116&sortby=4"
        product_category[str(cat4)] = "https://www.digikala.com/seller/aygzu/?category[0]=9467&category[1]=6269&category[2]=9781&pageno=1&last_filter=category&last_value=6269&sortby=4"

        # Add a new tab to the MDTabs Layout
        for i in range(len(list(product_category.keys()))):
            button = Button(text=(list(product_category.keys())[i]),
                size_hint_x= None, width= dp(170),
                font_name= "DroidNaskh-Regular.ttf",
                background_normal="blue.png", background_down="bluelight.jpg",
                )#border=(35, 35, 35, 35))

            button.bind(on_press=self.callback)

            self.ids.tab.add_widget(button)

        # Check if csv file wasnt save do web_scraping
        try:
            with open(filename) as csv_file:
                #print("in")
                reader = csv.reader(csv_file)
                for row in reader:
                    #print(row[1])
                    key_product_dict.append(row[0])
                    value_product_dict.append(row[1:6])

        except:
            mydir = os.getcwd()
            for f in os.listdir(mydir):
                if not f.endswith(".csv"):
                    continue
                os.remove(os.path.join(mydir, f))

            # First web scrsping
            self.web_scraping()

        self.step = "one"
        self.show()
        
    def show(self):

        # Initial values
        btn_list = []
        btn_img = []
        self.button_instance = OrderedDict()

        self.ids.scrollview.scroll_y = 1

        # Is first cat or not?
        if self.step == "one":
            cat = cat_list[0]
        else:
            cat = self.instance.text

        self.new_value_product_dict = list(filter(lambda c: c[2] == cat, value_product_dict))

        # Define number of dkp 
        #if int(self.new_value_product_dict[0][3]) < 100:
        #    range_2 = int(self.new_value_product_dict[0][3])
        #else:
        #    range_2 = 100
        range_2 = len(self.new_value_product_dict)

        # Add img and price button
        for j in range(range_2):
                
            # Named buttons as "btn1:btn50"
            btn_list.append("btn"+ str(j))
            btn_img.append("btn"+ str(j))

            # Define variable
            pr_1 = self.new_value_product_dict[j][0] 
            pr_2 = bidi_p3
            pr_3 = self.new_value_product_dict[j][1] 

            #print(cat)
            #print(self.new_value_product_dict[j][2])
            if pr_1 != "":

                # Create button 
                btn_list[j] = Button(text=f"[size=30]{pr_2}[/size] [size=60][b]{pr_1}[/b][/size]",
                    size_hint_x= None, width=dp(160), 
                    size_hint_y= None, height= dp(45),
                    pos_hint={'x': 0.02},
                    font_name= "DroidNaskh-Regular.ttf",
                    background_normal="blue.png", background_down="bluelight.jpg", markup= True,
                    border=(2, 2, 2, 2), color=(1, 1, 1, 1))

                btn_img[j] = Button(text="",
                    size_hint_x= None, width=dp(350), 
                    size_hint_y= None, height= dp(350),
                    pos_hint={'right': 0.99},
                    background_normal="img/%s.jpg"%(pr_3),  background_down="bluelight.png",)


                # Add buttons & images
                
                self.ids.main.add_widget(btn_img[j])
                #self.ids.main.add_widget(Image(source="img/%s.jpg"%(pr_3), size_hint= (1, 1)))#, height= dp(400)))
                self.ids.main.add_widget(btn_list[j])
                self.ids.main.add_widget(Label(text="", size_hint_y= None, height= dp(45)))

                # Create button instance to detect which button pressed
                self.button_instance[btn_list[j].__str__()] = j
                self.button_instance[btn_img[j].__str__()] = j

                # Defin function with bind for button
                btn_list[j].bind(on_press=self.on_press_button)
                btn_img[j].bind(on_press=self.on_press_button)
            else:
                continue

        self.step = "not_one"

    def callback(self, instance):
        self.instance = instance

        # Delete widgets
        children = self.ids.main.children
        ii = 0
        while ii < len(children):
            self.ids.main.remove_widget(children[ii])

        self.show()

    def on_press_button(self, args):
        webbrowser.open(self.new_value_product_dict[self.button_instance[str(args)]][4])

    def web_scraping(self):
        
        global key_product_dict
        global value_product_dict
        global Product_Dict     
        global pages_list

        # Initial values
        Product_Dict = OrderedDict()

        for category in cat_list:
    
            url = product_category[category]

            # Initial values
            n = 0
            DKP_list = []
            link_list = []
            price_list = []
            image_list = []
            pages_list = []

            while n >= 0: 
                
                # Requests & bs4
                r = requests.get(url)
                soup = BeautifulSoup(r.text, 'html.parser')

                # Find all
                images = soup.find_all('img', src=True)
                prices = soup.find_all('div', attrs={'class' : 'c-price__value-wrapper'})
                links = soup.find_all(class_= 'c-product-box__img c-promotion-box__image js-url js-product-item js-product-url', href=True)
                pages = soup.find_all(class_= 'c-pager__item', href=True)

                # Create DKP & link lists
                for link in links:
                    full_link = 'https://www.digikala.com' + link['href']
                    link_list.append(full_link)
                    string = str(link['href'])
                    match = re.search(r'dkp-.*/', string)
                    if match:
                        regex = '\d+'            
                        match1 = re.findall(regex, string[match.start():match.end()])
                        DKP_list.append(match1[0])

                # Create price list
                for price in prices:
                    number_2 = price.text.strip()                
                    price_list.append(convert_numbers.english_to_persian(convert_numbers.persian_to_english(number_2)))

                # Check if not saved create image link list
                for dkp in DKP_list:
                    try:
                        img = CoreImage("img/%s.jpg"%(dkp))
                    except:
                        print("DKP_list")
                        # Create image link list
                        for image in images:
                            match = re.search(r'/digikala-products/',str(image))
                            if match:
                                image_list.append(image['src'])
                        break
                    
                # Check if is first page create pages link
                if pages_list == []:
                    count = 0
                    for page in pages: 
                        count += 1
                        match = re.search(r'/search/', str(page['href']))
                        if match:
                            pages_link = 'https://www.digikala.com/seller/aygzu/' + str(page['href']).split('/search/')[1]
                            pages_list.append(pages_link)
                            n = len(pages_list) 
                            
                # Define "n" & url & len_category              
                n = n - 1
                if pages_list != []:
                    url = pages_list[n]


            for item in range (len(link_list)):

                # Check if image not saved, save it
                try:
                    im = CoreImage("img/%s.jpg"%(DKP_list[item]))
                except:
                    urllib.request.urlretrieve("%s"%(image_list[item]), "img/%s.jpg"%(DKP_list[item]))

                # Reshape persian font
                reshaped_p2 = arabic_reshaper.reshape("%s"%(price_list[item]))
                bidi_p2 = bidi.algorithm.get_display(reshaped_p2)

                #Create main dictionary
                Product_Dict[link_list[item]] = [bidi_p2, DKP_list[item], category, len(link_list), link_list[item]]

            # Create main dict keys
            key_product_dict = list(Product_Dict.keys())
            value_product_dict = list(Product_Dict.values())
        

        # writing to csv file 
        with open(filename, 'w') as csvfile: 

            # creating a csv writer object 
            writer = csv.writer(csvfile)

            # writing the data rows 
            for key, value in Product_Dict.items():
                writer.writerow([key, value[0], value[1], value[2], value[3], value[4]])

class RadinSport(App):
     def build(self):
         return MyLayout()

if __name__ == "__main__":
    RadinSport().run()