from bs4 import BeautifulSoup
import requests
import re
import time
import webbrowser

inFrom = input("Where would you like to travel from?\n")
inTo = input("Where would you like to travel to?\n")
inDate = re.sub(r'[^0-9]', "", str(input("When would you like to travel? Please use format DD/MM/YY\n")))
inTime = re.sub(r'[^0-9]', "", str(input("What time would you like to travel? Please use 24hr format, e.g. 17:30\n")))
inDepArr = str(input("And is the above time your prefferred arrival or departure time?\n"))[0:2]

URL = "https://ojp.nationalrail.co.uk/service/timesandfares/%s/%s/%s/%s/%s" % (inFrom, inTo, inDate, inTime, inDepArr)

response = requests.get(URL)

soup = BeautifulSoup(response.content, 'lxml')

cheapestFare = soup.find('td', class_="fare has-cheapest")
inputs = cheapestFare.findAll('input')
cheapestDetails = inputs[-1]
CSP = str(cheapestDetails).split("|")


costLabel = cheapestFare.find("label")
costLabelList = str(costLabel).split('>')
costWithDebris = costLabelList[2]
CWDC = re.sub(r'[^0-9]', '', costWithDebris)
costString = "£%s.%s" % (CWDC[0:-2], CWDC[-2:-1])
if len(costString.split('.')[1]) == 1:
    costString += "0"

fromStr = (CSP[0].split('"'))[-1]
fromAbr = CSP[1]
toStr = CSP[3]
toAbr = CSP[4]
depTimeStr = CSP[2]
arrTimeStr = CSP[5]


print("\nYou will be travelling from %s (%s) to %s (%s), leaving at %s, and arriving at %s. The price will be %s" % (fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString))
'''
print("opening:", URL)
webbrowser.open_new(URL)
ticketURL = "https://ojp.nationalrail.co.uk"
ticketURL += str(soup.find(id="journeyOption0")).split('"')[1]
ticketURL = re.sub("amp;", "", ticketURL)
time.sleep(4)
print("opening:", ticketURL)
webbrowser.open_new_tab(ticketURL)
'''