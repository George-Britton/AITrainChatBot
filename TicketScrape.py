from bs4 import BeautifulSoup
import requests
import re

# this function turns the passed in data into the correct format for webscraping
def SanitizeInput(fromSta, toSta, travelDate, travelTime, arriveDepart):
    outFromSta = re.sub(r'[^a-zA-Z]', "", str(fromSta)) # cleanse the departure station
    outToSta = re.sub(r'[^a-zA-Z]', "", str(toSta)) # cleanse the arrival station
    outTravelDate =  re.sub(r'[^0-9]', "", str(travelDate)) # cleanse the travel date
    outTravelTime = re.sub(r'[^0-9]', "", str(travelTime)) # cleanse the travel time
    # set whether the time supplied is arrival or departure
    if arriveDepart:
        outArriveDepart = "arr"
    else:
        outArriveDepart = "dep"
    return outFromSta, outToSta, outTravelDate, outTravelTime, outArriveDepart


# this function scrapes the web for the required webpage and turns it into a parsed format
def ScrapeWeb(URL):
    response = requests.get(URL) # get the webpage to scrape
    soup = BeautifulSoup(response.content, 'lxml') # parse the webpage with beautiful soup
    return soup


# get the monetary cost of the cheapest found fare
def GetCheapestFareCost(cheapestFare):
    costLabel = cheapestFare.find("label") # find the cost label
    costLabelList = str(costLabel).split('>') # split the cost label into list
    costWithDebris = costLabelList[2] # trim the cost list
    CWDC = re.sub(r'[^0-9]', '', costWithDebris) # cleanse the cost list
    costString = "£%s.%s" % (CWDC[0:-2], CWDC[-2:-1]) # get cost
    if len(costString.split('.')[1]) == 1: # make cost readable format
        costString += "0"
    return costString


# get a list of the details of the cheapest fare
def GetCheapestFareDetailsFromWebpage(soup):
    cheapestFare = soup.find('td', class_="fare has-cheapest") # find the cheapest fare
    inputs = cheapestFare.findAll('input') # get display data
    cheapestDetails = inputs[-1] # cleanse display data
    CSD = str(cheapestDetails).split("|") # separate display data
    costString = GetCheapestFareCost(cheapestFare)
    return CSD, costString
    

# picks the only required details from the cheapest fare details list
def GetRequiredFareDetails(cheapestDetails):
    fromStr = (cheapestDetails[0].split('"'))[-1] # get from station
    fromAbr = cheapestDetails[1] # get from station abbreviation
    toStr = cheapestDetails[3] # get to station
    toAbr = cheapestDetails[4] # get to station abbreviation
    depTimeStr = cheapestDetails[2] # get departure time
    arrTimeStr = cheapestDetails[5] # get arrival time
    return fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr


#fromSta = the departure station, toSta = the arrival station, inDate = the date of travel (DDMMYY),
#inTime = the time of travel (24hr), inArrive = bool true if time is desired arrival time, false if time is desired departure time
def FindTicket(inFromSta, inToSta, inDate, inTime, inArrive):
    fromSta, toSta, travelDate, travelTime, arriveDepart = SanitizeInput(inFromSta, inToSta, inDate, inTime, inArrive) # cleanse the webscraping parameters
    URL = "https://ojp.nationalrail.co.uk/service/timesandfares/%s/%s/%s/%s/%s" % (fromSta, toSta, travelDate, travelTime, arriveDepart) # create the webscraping link
    soup = ScrapeWeb(URL) # get parsed webpage
    cheapestDetails, costString = GetCheapestFareDetailsFromWebpage(soup) # get cheapest fare details and cost
    fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr = GetRequiredFareDetails(cheapestDetails) # get printable fare details
    
    # return details and URL
    return fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL
    

#fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL = FindTicket("norwich", "London", "080121", "1200", True)
#print("\nYou will be travelling from %s (%s) to %s (%s), leaving at %s, and arriving at %s. The price will be %s" % (fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString))
#print("\n", URL)