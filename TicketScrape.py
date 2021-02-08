from bs4 import BeautifulSoup
import requests
import re
import time

# this function turns the passed in data into the correct format for webscraping
def SanitizeInput(fromSta, toSta, travelDate, travelTime, arriveDepart, returnDate):
    outFromSta = re.sub(r'[^a-zA-Z]', "", str(fromSta)) # cleanse the departure station
    outToSta = re.sub(r'[^a-zA-Z]', "", str(toSta)) # cleanse the arrival station
    outTravelDate =  re.sub(r'[^0-9a-zA-Z]', "", str(travelDate)) # cleanse the travel date
    outTravelTime = re.sub(r'[^0-9a-zA-Z]', "", str(travelTime)) # cleanse the travel time
    outReturnDate =  re.sub(r'[^0-9a-zA-Z]', "", str(returnDate)) # cleanse the travel date
    # set whether the time supplied is arrival or departure
    if arriveDepart:
        outArriveDepart = "arr"
    else:
        outArriveDepart = "dep"
    return outFromSta, outToSta, outTravelDate, outTravelTime, outArriveDepart, outReturnDate


# this function scrapes the web for the required webpage and turns it into a parsed format
def ScrapeWeb(URL):
    response = requests.get(URL) # get the webpage to scrape
    soup = BeautifulSoup(response.content, features="lxml") # parse the webpage with beautiful soup
    return soup


# get the monetary cost of the cheapest found fare for a single
def GetCheapestSingleFareCost(cheapestFare):
    costLabel = cheapestFare.find("label") # find the cost label
    costLabelList = str(costLabel).split('>') # split the cost label into list
    costWithDebris = costLabelList[2] # trim the cost list
    costRaw = re.sub(r'[^0-9]', '', costWithDebris) # cleanse the cost list
    costString = "£%s.%s" % (costRaw[0:-2], costRaw[-2:-1]) # get cost
    if len(costString.split('.')[1]) == 1: # make cost readable format
        costString += "0"
    return costString


# get the monetary cost of the cheapest found fare for a return
def GetCheapestReturnFareCost(cheapestFare):
    rawCostList = str(cheapestFare).split(" ") # split up the soup to isolate the cost
    costString = rawCostList[rawCostList.index("£") + 1].split("\\")[-1] # find the cost index
    costString = costString[0:5] # isolate cost
    costString = "£" + costString # add pound sign
    return costString


# get a list of the details of the cheapest fare
def GetCheapestFareDetailsFromWebpage(soup, isReturn):
    if isReturn:
        cheapestFare = soup.find_all('td', class_="fare has-cheapest") # find the cheapest fare details
        costFinder = soup.find_all('button', class_="b-y lrg not-IE6") # find the cheapest fare cost
        costString = GetCheapestReturnFareCost(costFinder) # get the fare cost
        cheapestOutDetails = cheapestFare[0].find("script") # get the outward details
        cheapestBackDetails = cheapestFare[0].find("script") # get the return details
        cheapestDetailsString = str(cheapestOutDetails) + str(cheapestBackDetails) # concatonate details
    else:
        cheapestFare = soup.find('td', class_="fare has-cheapest") # find the cheapest fare
        inputs = cheapestFare.find_all('input') # get display data
        cheapestDetails = inputs[-1] # cleanse display data
        cheapestDetailsString = str(cheapestDetails).split("|") # separate display data
        costString = GetCheapestSingleFareCost(cheapestFare) # get the fare cost
    return cheapestDetailsString, costString
    

# picks the only required details from the cheapest fare details list for a single
def GetRequiredSingleFareDetails(cheapestDetails):
    fromStr = (cheapestDetails[0].split('"'))[-1] # get from station
    fromAbr = cheapestDetails[1] # get from station abbreviation
    toStr = cheapestDetails[3] # get to station
    toAbr = cheapestDetails[4] # get to station abbreviation
    depTimeStr = cheapestDetails[2] # get departure time
    arrTimeStr = cheapestDetails[5] # get arrival time
    return fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr


# picks the only required details from the cheapest fare details list for a single
def GetRequiredReturnFareDetails(cheapestDetails):
    cheapestDetailsList = cheapestDetails.split('"')
    for item in cheapestDetailsList:
        if ',' in item or ':' in item or '(' in item or ')' in item or '/' in item or '\\' in item:
            cheapestDetailsList.remove(item)
    outFromSta = cheapestDetailsList[cheapestDetailsList.index('departureStationName') + 1] # get outward from station
    outFromStaAbr = cheapestDetailsList[cheapestDetailsList.index('departureStationCRS') + 1] # get outward from station abbreviation
    outToSta = cheapestDetailsList[cheapestDetailsList.index('arrivalStationName') + 1] # get outward to station
    outToStaAbr = cheapestDetailsList[cheapestDetailsList.index('arrivalStationCRS') + 1] # get outward to station abbreviation
    outDepTime = cheapestDetailsList[cheapestDetailsList.index('departureTime') + 1] # get outward departure time
    outArrTime = cheapestDetailsList[cheapestDetailsList.index('arrivalTime') + 1] # get outward arrival time
    del cheapestDetailsList[0:20]
    backFromSta = cheapestDetailsList[cheapestDetailsList.index('departureStationName') + 1] # get return from station
    backFromStaAbr = cheapestDetailsList[cheapestDetailsList.index('departureStationCRS') + 1] # get return from station abbreviation
    backToSta = cheapestDetailsList[cheapestDetailsList.index('arrivalStationName') + 1] # get return to station
    backToStaAbr = cheapestDetailsList[cheapestDetailsList.index('arrivalStationCRS') + 1] # get return to station abbreviation
    backDepTime = cheapestDetailsList[cheapestDetailsList.index('departureTime') + 1] # get return departure time
    backArrTime = cheapestDetailsList[cheapestDetailsList.index('arrivalTime') + 1] # get return arrival time
    return outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime



# create the URL suffix required to search for a return ticket
def AddReturn(inRetDate, inRetTime, inRetArrive):
    outRetDate =  re.sub(r'[^0-9a-zA-Z]', "", str(inRetDate)) # cleanse the return date
    outRetTime = re.sub(r'[^0-9]', "", str(inRetTime)) # cleanse the return time
    outSuffix = "/%s/%s/" % (outRetDate, outRetTime)
    # sets whether the time supplied is arrival or departure
    if inRetArrive:
        outSuffix += "arr"
    else:
        outSuffix += "dep"
    return outSuffix

#fromSta = the departure station, toSta = the arrival station, inDate = the date of travel (DDMMYY),
#inTime = the time of travel (24hr), inArrive = bool true if time is desired arrival time, false if time is desired departure time
def FindTicket(inFromSta, inToSta, inDate, inReturn=False, inRetDate="tomorrow", inTime="2345", inArrive=True, inRetTime="2345", inRetArrive=True):
    fromSta, toSta, travelDate, travelTime, arriveDepart, returnDate = SanitizeInput(inFromSta, inToSta, inDate, inTime, inArrive, inRetDate) # cleanse the webscraping parameters
    URL = "https://ojp.nationalrail.co.uk/service/timesandfares/%s/%s/%s/%s/%s" % (fromSta, toSta, travelDate, travelTime, arriveDepart) # create the webscraping link
    # adds the return details if the user wants a return ticket
    if inReturn:
        URL += AddReturn(returnDate, inRetTime, inRetArrive)
    soup = ScrapeWeb(URL) # get parsed webpage
    cheapestDetails, costString = GetCheapestFareDetailsFromWebpage(soup, inReturn) # get cheapest fare details and cost
    if inReturn:
        outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime = GetRequiredReturnFareDetails(cheapestDetails)
        # return outFromSta, outToSta, outDepTime, outArrTime, costString, URL
        return outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime, costString, URL
    else:
        fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr = GetRequiredSingleFareDetails(cheapestDetails) # get printable fare details
        # return details and URL
        return fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL
        # return fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL
  
#
##
### EXAMPLES:
##
#
# SINGLE
# fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL = FindTicket("manchester", "derby", "tomorrow")
# print("\nYou will be travelling from %s (%s) to %s (%s), leaving at %s, and arriving at %s. The price will be %s" % (fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString))
# print("\n", URL)

# RETURN
# outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime, costString, URL = FindTicket("norwich", "ipswich", "tomorrow", True, "11022021", "1200", True, "1200", True)
# print("You will be leaving from %s (%s) to %s (%s) at %s, and arriving at %s. Your return trip will be from %s (%s), to %s (%s) at %s, arriving at %s. The cost will be %s" % (outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime, costString))
# print("\n", URL)
