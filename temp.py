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
import urllib.request as urllib2




url = "https://www.digikala.com/seller/aygzu/"
x = urllib.request.urlopen(url)
soup = BeautifulSoup(x.read())

#headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

#r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})

#soup = BeautifulSoup(r.text, 'html.parser')


prices = soup.find_all('div', attrs={'style' : 'width: 240px; height: 240px;'})
print(prices)