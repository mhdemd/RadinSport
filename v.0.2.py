from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.graphics import BorderImage
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.button import MDRoundFlatIconButton
from kivy.core.image import Image as CoreImage


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


# GUI
KV = """
#:import arabic_reshaper arabic_reshaper
#:import get_display bidi.algorithm.get_display
#:import gch kivy.utils.get_color_from_hex
#:import webbrowser webbrowser


BoxLayout:
    orientation: 'vertical'
    canvas:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bc.jpg'

    MDToolbar:
        title: 'Radin Sport'
        md_bg_color: gch('#1A237E')
        height:80
        elevation: 10
        left_action_items: [["menu", lambda x: x]]
        right_action_items: [["dots-vertical", lambda x: x]]

    MDTabs:
        id: tabs
        font_name: "DroidNaskh-Regular.ttf"
        background_color: gch('#9FA8DA')
        text_color_normal: gch('#000000')
        text_color_active: gch('#1A237E')
        tab_indicator_height: 7
        tab_indicator_anim: True
        #tab_hint_x: True
        indicator_color: gch('#1A237E')
        on_tab_switch: app.on_tab_switch(*args)

    BoxLayout:
        size_hint_y: 10
        size_hint_x: 1.05
                
        ScrollView:
            id: scrollview
            on_scroll_stop: app.on_scroll_stop()
            scroll_wheel_distance: 5
            smooth_scroll_end: 1

            MDGridLayout:
                id: box
                markup: True
                cols: 2

                row_default_height: (self.width - self.cols*self.spacing[0]) / self.cols
                row_force_default: True
                adaptive_height: True
                padding: dp(4), dp(0)
                spacing: dp(50)

          
"""
class Tab(MDFloatLayout, MDTabsBase):
    """Class implementing content for a tab."""


class RadinSport(MDApp):

    global cat_list
    global product_category
    
    
    # Define dictionaries
    product_category = OrderedDict()

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

        # Upload file to folder
        #folder = m.find('radinsport')
        #m.upload(filename, folder[0])
        

    def on_scroll_stop(self):
        
        category = str(new_value_product_dict[0][2])
        temp = list(filter(lambda c: c[2] == category, new_value_product_dict))
        #print(self.root.ids.scrollview.vbar[0])
        if int(temp[0][3]) == len(btn_list):
            pass

        elif self.root.ids.scrollview.vbar[0] < 0.005:
            
            #self.root.ids.scrollview.scroll_y = 0
        
            if int(temp[0][3]) - len(btn_list) < 1:
                range_2 = int(new_value_product_dict[0][3]) - len(btn_list)
            else:
                range_2 = len(btn_list) + 1

            len_btn = len(btn_list) + 1
            for j in range(len(btn_list), range_2):
                # Named buttons as "btn1:btn50"
                btn_list.append("btn"+ str(j + len_btn))

                # Define variable
                pr_1 = new_value_product_dict[j][0] 
                pr_2 = bidi_p3
                pr_3 = new_value_product_dict[j][1]

                # Create button 
                btn_list[j] = MDRoundFlatIconButton(icon= "cart-plus", icon_color=[26/255, 35/255, 126/255, 1], \
                line_color=[26/255, 35/255, 126/255, 1] , text=f"[size=26]{pr_2}[/size] [size=36][b]{pr_1}[/b][/size]", 
                text_color=[26/255, 35/255, 126/255, 1], md_bg_color=[26/255, 35/255, 126/255, 1], font_size= '6dp' ,\
                line_width=1.02, font_name= "DroidNaskh-Regular.ttf"  )

                # Add buttons & imageslen(btn_list)
                self.root.ids.box.add_widget(btn_list[j])
                self.root.ids.box.add_widget(Image(source="img/%s.jpg"%(pr_3)))

                # Create button instance to detect which button pressed
                button_instance[btn_list[j].__str__()] = j

                # Defin function with bind for button
                btn_list[j].bind(on_press=self.on_press_button)


    def build(self):
        return Builder.load_string(KV)


    def on_press_button(self, args):

        webbrowser.open(new_value_product_dict[button_instance[str(args)]][4])
       

    def on_start(self):
        global btn_list
        global filename
        global bidi_p3
        global key_product_dict
        global value_product_dict
        global button_instance
        global new_value_product_dict

        # Initial values
        btn_list = []
        key_product_dict = []
        value_product_dict = []
        button_instance = OrderedDict()

        # Reshape font
        reshaped_p3 = arabic_reshaper.reshape("تومان")
        bidi_p3 = bidi.algorithm.get_display(reshaped_p3)

        # name of csv file 
        today = date.today()
        date_today = today.strftime("%b-%d-%Y")
        filename = "%s.csv"%(date_today)

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
        
        # Add a new tab to the MDTabs Layout
        for i in range(len(list(product_category.keys()))):
            self.root.ids.tabs.add_widget(Tab(title=(list(product_category.keys())[i])))
       
        if int(value_product_dict[0][3]) < 4:
            range_2 = int(value_product_dict[0][3])
        else:
            range_2 = 4

        for j in range(range_2):

            # Named buttons as "btn1:btn50"
            btn_list.append("btn"+ str(j))

            # Define variable
            pr_1 = value_product_dict[j][0] 
            pr_2 = bidi_p3
            pr_3 = value_product_dict[j][1]

            # Create button 
            btn_list[j] = MDRoundFlatIconButton(icon= "cart-plus", icon_color=[26/255, 35/255, 126/255, 1], \
            line_color=[26/255, 35/255, 126/255, 1] , text=f"[size=26]{pr_2}[/size] [size=36][b]{pr_1}[/b][/size]", 
            text_color=[26/255, 35/255, 126/255, 1], md_bg_color=[26/255, 35/255, 126/255, 1], font_size= '6dp' ,\
            line_width=1.02, font_name= "DroidNaskh-Regular.ttf"  )

            # Add buttons & images
            self.root.ids.box.add_widget(btn_list[j])
            self.root.ids.box.add_widget(Image(source="img/%s.jpg"%(pr_3)))

            # Create button instance to detect which button pressed
            button_instance[btn_list[j].__str__()] = j

            # Defin function with bind for button
            btn_list[j].bind(on_press=self.on_press_button)
        
            new_value_product_dict = value_product_dict

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text): 
        """Called when the tab is switched.

        :type instance_tabs: <kivymd.uix.tab.MDTabs object>;
        :param instance_tab: <__main__.Tab object>;
        :param instance_tab_label: <kivymd.uix.tab.MDTabsLabel object>;
        :param tab_text: text or name icon of tab;
        """
        global range_category
        global new_value_product_dict
        global btn_list
        global button_instance

        btn_list = []
        button_instance = OrderedDict()

        # Initial values
        new_value_product_dict = []

        self.root.ids.scrollview.scroll_y = 1

        # Delete widgets
        children = self.root.ids.box.children
        ii = 0
        while ii < len(children):
            self.root.ids.box.remove_widget(children[ii])


        new_value_product_dict = list(filter(lambda c: c[2] == str(tab_text), value_product_dict))


        if int(new_value_product_dict[0][3]) < 4:
            range_2 = int(new_value_product_dict[0][3])
        else:
            range_2 = 4

        for j in range(range_2):

            # Named buttons as "btn1:btn50"
            btn_list.append("btn"+ str(j))

            # Define variable
            pr_1 = new_value_product_dict[j][0] 
            pr_2 = bidi_p3
            pr_3 = new_value_product_dict[j][1]

            # Create button 
            btn_list[j] = MDRoundFlatIconButton(icon= "cart-plus", icon_color=[26/255, 35/255, 126/255, 1], \
            line_color=[26/255, 35/255, 126/255, 1] , text=f"[size=26]{pr_2}[/size] [size=36][b]{pr_1}[/b][/size]", 
            text_color=[26/255, 35/255, 126/255, 1], md_bg_color=[26/255, 35/255, 126/255, 1], font_size= '6dp' ,\
            line_width=1.02, font_name= "DroidNaskh-Regular.ttf"  )

            # Add buttons & images
            self.root.ids.box.add_widget(btn_list[j])
            self.root.ids.box.add_widget(Image(source="img/%s.jpg"%(pr_3)))

            # Create button instance to detect which button pressed
            button_instance[btn_list[j].__str__()] = j

            # Defin function with bind for button
            btn_list[j].bind(on_press=self.on_press_button)
        

RadinSport().run()
