from bs4 import BeautifulSoup
import requests
import re

fromSta = input("What station are you trying to get from? ")
toSta = input("What station are you trying to get to? ")

Dep = fromSta.split(" ")
Arr = toSta.split(" ")
if Dep[-1].upper() != "STATION":
    fromSta += "+Station"
if Arr[-1].upper() != "STATION":
    toSta += "+Station"

Dep = fromSta.replace(" ", "+")
Arr = toSta.replace(" ", "+")

URL = "https://www.google.com/maps/dir/%s/%s" % (Dep, Arr)

response = requests.get(URL)

soup = BeautifulSoup(response.content, 'lxml')

print(soup)