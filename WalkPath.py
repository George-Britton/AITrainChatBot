from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession
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

session = AsyncHTMLSession()

async def get_URL():
    response = await asession.get(URL)

response.html.render()

soup = BeautifulSoup(response.html.html, 'html')

images = soup.findAll('a')

print(images)