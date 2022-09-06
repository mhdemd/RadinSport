from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as ImageWidget
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.image import AsyncImage
#from kivy.uix.floatlayout import FloatLayout

import PIL
from PIL import Image
import urllib.request
import re
import requests
import webbrowser
from selenium import webdriver
import convert_numbers
import arabic_reshaper
from bs4 import BeautifulSoup
from collections import  OrderedDict
from bidi.algorithm import get_display
import bidi
import csv 
from datetime import date
import os

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

        global st
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
        cat1 = get_display(arabic_reshaper.reshape("کلاه و نقاب"))
        cat2 = get_display(arabic_reshaper.reshape("قمقمه و شیکر"))
        cat3 = get_display(arabic_reshaper.reshape("دستکش ها و لوازم بدنسازی"))
        cat4 = get_display(arabic_reshaper.reshape("حوله و مایو"))
        cat_list = [cat1, cat2, cat3, cat4]

        # Define Category link
        product_category[str(cat1)] = "https://www.digikala.com/seller/aygzu/?category[0]=9539&category[1]=9938&pageno=1&sortby=4"
        product_category[str(cat2)] = "https://www.digikala.com/seller/aygzu/?category[0]=6102&pageno=1&last_filter=category&last_value=6102&sortby=4"
        product_category[str(cat3)] = "https://www.digikala.com/seller/aygzu/?category[0]=6116&category[1]=9524&category[2]=6432&category[3]=9428&category[4]=9551&pageno=1&last_filter=category&last_value=6116&sortby=4"
        product_category[str(cat4)] = "https://www.digikala.com/seller/aygzu/?category[0]=9467&category[1]=6269&category[2]=9781&pageno=1&last_filter=category&last_value=6269&sortby=4"

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

            if self.web_scraping() == False:
                self.mgr1.current = "fifth screen"

            else:
                self.step = "one"
                self.mgr1.current = "one screen"
                try:
                    if self.pop_up:
                        self.pop_up.dismiss()
                except:
                    pass
        try:
            self.pop_up.dismiss()
        except:
            pass

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
                try:
                    #r = requests.get(url)
                    browser=webdriver.Firefox()
                    browser.get(url)
                    html = browser.page_source
                    browser.close()
                except:
                    return False

                soup = BeautifulSoup(html, 'html.parser')

                # Find all
                images = soup.find_all('img', src=True)
                prices = soup.find_all('div', attrs={'class' : 'c-price__value-wrapper'})
                links = soup.find_all(class_= 'c-product-box__img c-promotion-box__image js-url js-product-item js-product-url', href=True)
                pages = soup.find_all(class_= 'c-pager__item', href=True)

                print(len(images))
                print(len(prices))
                print(len(links))
                print(len(pages))


                # Create DKP & link lists
                for link in links:
                    print("len(links)")
                    full_link = 'https://www.digikala.com' + link['href']
                    link_list.append(full_link)
                    string = str(link['href'])
                    match = re.search(r'dkp-.*/', string)
                    if match:
                        regex = '\d+'            
                        match1 = re.findall(regex, string[match.start():match.end()])
                        DKP_list.append(match1[0])
                        #print(len(DKP_list)+10000000)

                # Create price list
                for price in prices:
                    number_2 = price.text.strip()    
                    price_list.append(number_2.split("تومان")[0].strip())
                    #price_list.append(convert_numbers.english_to_persian(convert_numbers.persian_to_english(number_2)))

                # Check if not saved create image link list
                count = 0
                for dkp in DKP_list:
                    try:
                        img = CoreImage("img/%s.jpg"%(dkp))
                    except:
                        if image_list == []:
                            for image in images:
                                match = re.search(r'/digikala-products/',str(image))
                                if match:
                                    image_list.append(image['src'])
                
                        urllib.request.urlretrieve("%s"%(image_list[count]), "img/%s.jpg"%(dkp))
                    
                    count += 1

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
                #try:
                #    im = CoreImage("img/%s.jpg"%(DKP_list[item]))
                #except:
                #    urllib.request.urlretrieve("%s"%(image_list[item]), "img/%s.jpg"%(DKP_list[item]))

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

        return value_product_dict

    def web_scaping_details(self, url):
        
        global list_detail

        list_detail = []

        # Requests & bs4
        try:
            r = requests.get(url)
        except:
            return False

        soup = BeautifulSoup(r.text, 'html.parser')

        product_name = soup.find_all('div', attrs={'class' : 'c-product__title-container'})
        #print(product_name[0].text.strip() ) 
        list_detail. append(product_name[0].text.strip()) 

        price_two = soup.find_all('div', attrs={'class' : 'c-product__seller-price-pure js-price-value'})
        #print(price_two[0].text.strip() )
        list_detail.append(price_two[0].text.strip()) 
        pr2 = price_two[0].text.strip()

        price_one = soup.find_all('div', attrs={'class' : 'c-product__seller-price-info'})
        st = price_one[1].text.strip()
        st = st.split("\n")
        check = st[0].strip()
        off = st[2].strip()

        if check == pr2:
            list_detail.append("0")
            list_detail.append("0")
        else: 
            list_detail.append(check)
            list_detail.append(off)

        image_list = []
        img = soup.find_all('div', attrs={'class' : 'c-remodal-gallery__content is-active js-gallery-tab-content'})
        list = str(img[0]).split('"')
        for image in list:
            match = re.search(r'q_80',str(image))
            if match:
                if image not  in image_list:
                    image_list.append(image)
                    #print(image)
                    list_detail.append(image)
                    
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
        
        # Get url
        self.url = self.new_value_product_dict[j][4]
        
        # Web scraping
        if self.web_scaping_details(self.url) == False:
            self.mgr1.current = "fifth screen"
            if self.pop_up:
                self.pop_up.dismiss()

        else:
            # Get category
            self.cat = self.new_value_product_dict[j][2]
            
            # Get price1
            price1 = list_detail[2]
            
            # Get price2
            price2 = list_detail[1]
            
            # Get off
            off =  list_detail[3]

            # Get name
            name = list_detail[0]
            name_list = name.split("\n")
            if len(name_list) > 1:
                name = name_list[0].strip() + name_list[1].strip()
            name_list = name.split("غیر اصل")
            if len(name_list) > 1:
                name = name_list[0].strip() + name_list[1].strip()

            # Change current screen
            self.mgr1.current= "forth screen"
            
            # Add title
            self.mgr1.title_dt.text= "%s"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s"%(name))))
            len_title= len(name)

            if len_title < 44:
                self.mgr1.title_dt.font_size= 55
            else:
                self.mgr1.title_dt.font_size= 45
    #ok
            # Add image to Carousel
            self.mgr1.image_dt.clear_widgets()

            try: 
                img = Image.open("img/%s_1600.jpg"%(self.new_value_product_dict[j][1]))
            except:
                img = Image.open("img/%s.jpg"%(self.new_value_product_dict[j][1]))
                new_imge = img.resize((1600, 1600), PIL.Image.ANTIALIAS)
                new_imge.save("img/%s_1600.jpg"%(self.new_value_product_dict[j][1]), quality=80)
    ##
            image = AsyncImage(source= "img/%s_1600.jpg"%(self.new_value_product_dict[j][1]), size_hint=(None, None),
                size=(self.width,  self.width) )
            self.mgr1.image_dt.add_widget(image)

            for i in range(len(list_detail) - 4):
                image = AsyncImage(source=list_detail[i + 4], size_hint=(None, None),
                size=(self.width,  self.width)
                )
                self.mgr1.image_dt.add_widget(image)
    #ok
            # Add price1 label
            toman = "تومان"
            if price1 != "0":
                #text1 = "[size=40]%s[/size]"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s %s"%(price1, toman))))
                text1 = "%s"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s "%(price1 ))))

            else:
                text1 = ""
            self.mgr1.price1_dt.text = text1

            # Add price2 label
            #text2 = "[size=55]%s[/size]"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s %s"%(price2, toman))))
            text2 = "%s"%(bidi.algorithm.get_display(arabic_reshaper.reshape("%s %s"%(price2, toman))))
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

        self.new_value_product_dict = list(filter(lambda c: c[2] == cat, value_product_dict))

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

            pr_2 = bidi_p3

            ################# img1
            pr_1_1 = self.new_value_product_dict[j1][0]
            pr_3_1 = self.new_value_product_dict[j1][1] 

            try:
                img = CoreImage("img/%s_resize_min.jpg"%(pr_3_1))
            except:
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
            ################# Label1

            btn_list[j1] = Button(background_normal=("img_price.jpg"), background_down=("img_price.jpg"),
                    color= (0, 0, 0),
                    text=f"{pr_2} {pr_1_1}",
                    font_name= "XB Niloofar.ttf",
                    size_hint=(None, None),
                    size=((self.width )/4, self.height/30), pos_hint= {"center_x": .5},
                )

            self.mgr1.main.add_widget(btn_list[j1])
            self.mgr1.main.add_widget(Label(text="", size_hint=(None, None),
                size=((self.width )/4, self.height/30), pos_hint= {"center_x": .5}))
            #self.button_instance[btn_list[j1].__str__()] = j1
            #btn_list[j1].bind(on_press=self.on_press_button)
            ################# img2
            if j2 != " ": 
                pr_1_2 = self.new_value_product_dict[j2][0]
                pr_3_2 = self.new_value_product_dict[j2][1] 

                try:
                    img = CoreImage("img/%s_resize_min.jpg"%(pr_3_2))
                except:
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
            ################# Label2
            if j2 != " ": 
                btn_list[j2] = Button(background_normal=("img_price.jpg"), background_down=("img_price.jpg"),
                    color= (0, 0, 0),
                    text=f"{pr_2} {pr_1_2}",
                    font_name= "XB Niloofar.ttf",
                    size_hint=(None, None),
                    size=((self.width )/4, self.height/30), pos_hint= {"center_x": .5}
                    )  
                self.mgr1.main2.add_widget(btn_list[j2])
                self.mgr1.main2.add_widget(Label(text="", size_hint=(None, None),
                    size=((self.width )/4, self.height/30), pos_hint= {"center_x": .5}))
                #self.button_instance[btn_list[j2].__str__()] = j2
                #btn_list[j2].bind(on_press=self.on_press_button)
            else: 
                btn_list = Label(
                    text="",
                    font_name= "XB Niloofar.ttf",
                    size_hint=(None, None),
                    size=((self.width )/4, self.height/30), pos_hint= {"center_x": .5}
                    )  
                self.mgr1.main2.add_widget(btn_list)
                self.mgr1.main2.add_widget(Label(text="", size_hint=(None, None),
                    size=((self.width )/4, self.height/30), pos_hint= {"center_x": .5}))

            ################# img3on_press_button
            if j3 != " ": 
                pr_1_3 = self.new_value_product_dict[j3][0]
                pr_3_3 = self.new_value_product_dict[j3][1]

                try:
                    img = CoreImage("img/%s_resize_min.jpg"%(pr_3_3))
                except:
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
            
            ################# Label3
            if j3 != " ": 
                btn_list[j3] = Button(background_normal=("img_price.jpg"), background_down=("img_price.jpg"),
                    color= (0, 0, 0),
                    text=f"{pr_2} {pr_1_3}",
                    font_name= "XB Niloofar.ttf",
                    size_hint=(None, None),
                    size=((self.width )/4, self.height/30), pos_hint= {"center_x": .5}
                    ) 
                self.mgr1.main3.add_widget(btn_list[j3])
                self.mgr1.main3.add_widget(Label(text="", size_hint=(None, None),
                    size=((self.width )/4, self.height/30), pos_hint= {"center_x": .5}))
                #self.button_instance[btn_list[j3].__str__()] = j3
                #btn_list[j3].bind(on_press=self.on_press_button)
            
            else:
                btn_list = Label(
                    text= "",
                    font_name= "XB Niloofar.ttf",
                    size_hint=(None, None),
                    size=((self.width )/4, self.height/30), pos_hint= {"center_x": .5}
                    ) 
                self.mgr1.main3.add_widget(btn_list)
                self.mgr1.main3.add_widget(Label(text="", size_hint=(None, None),
                    size=((self.width )/4, self.height/30), pos_hint= {"center_x": .5}))
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
