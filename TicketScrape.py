from bs4 import BeautifulSoup
import requests
import re
import time

# this function turns the passed in data into the correct format for webscraping
def SanitizeInput(fromSta, toSta, travelDate, travelTime, arriveDepart, returnDate):
    outFromSta = re.sub(r'[^a-zA-Z]', "", str(fromSta)) # cleanse the departure station
    outToSta = re.sub(r'[^a-zA-Z]', "", str(toSta)) # cleanse the arrival station
    outTravelDate =  re.sub(r'[^0-9a-zA-Z]', "", str(travelDate)) # cleanse the travel date
    outTravelTime = re.sub(r'[^0-9]', "", str(travelTime)) # cleanse the travel time
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
    soup = BeautifulSoup(response.content, features="html") # parse the webpage with beautiful soup
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
    outCostWithDebris = cheapestFare[0].find_all("label", class_="opreturn")[-1]
    outCostRaw = str(outCostWithDebris).split("£")[-1]
    outCost = outCostRaw.split("<")[0]
    backCostWithDebris = cheapestFare[1].find_all("label", class_="opreturn")[-1]
    backCostRaw = str(backCostWithDebris).split("£")[-1]
    backCost = backCostRaw.split("<")[0]
    outCostPence = int(re.sub(r'[^0-9]', '', outCost))
    backCostPence = int(re.sub(r'[^0-9]', '', backCost))
    totalCostPence = str(outCostPence + backCostPence)
    costString = "£" + totalCostPence[0:-2] + "." + totalCostPence[-2:-1]
    if len(costString.split(".")[-1]) == 1:
        costString += "0"
    return costString


# get a list of the details of the cheapest fare
def GetCheapestFareDetailsFromWebpage(soup, isReturn):
    if isReturn:
        cheapestFare = soup.find_all('td', class_="fare has-cheapest") # find the cheapest fare
        costString = GetCheapestReturnFareCost(cheapestFare)
        cheapestOutDetails = cheapestFare[0].find("script")
        cheapestBackDetails = cheapestFare[1].find("script")
        cheapestDetailsString = str(cheapestOutDetails) + str(cheapestBackDetails)
    else:
        cheapestFare = soup.find('td', class_="fare has-cheapest") # find the cheapest fare
        inputs = cheapestFare.find_all('input') # get display data
        cheapestDetails = inputs[-1] # cleanse display data
        cheapestDetailsString = str(cheapestDetails).split("|") # separate display data
        costString = GetCheapestSingleFareCost(cheapestFare)
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
    outFromSta = cheapestDetailsList[9] # get outward from station
    outFromStaAbr = cheapestDetailsList[13] # get outward from station abbreviation
    outToSta = cheapestDetailsList[17] # get outward to station
    outToStaAbr = cheapestDetailsList[21] # get outward to station abbreviation
    outDepTime = cheapestDetailsList[27] # get outward departure time
    outArrTime = cheapestDetailsList[31] # get outward arrival time
    backFromSta = cheapestDetailsList[201] # get return from station
    backFromStaAbr = cheapestDetailsList[205] # get return from station abbreviation
    backToSta = cheapestDetailsList[209] # get return to station
    backToStaAbr = cheapestDetailsList[213] # get return to station abbreviation
    backDepTime = cheapestDetailsList[221] # get return departure time
    backArrTime = cheapestDetailsList[225] # get return arrival time
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
def FindTicket(inFromSta, inToSta, inDate, inReturn=False, inRetDate="tomorrow", inTime="1200", inArrive=True, inRetTime="1200", inRetArrive=True):
    fromSta, toSta, travelDate, travelTime, arriveDepart, inRetDate = SanitizeInput(inFromSta, inToSta, inDate, inTime, inArrive, inRetDate) # cleanse the webscraping parameters
    URL = "https://ojp.nationalrail.co.uk/service/timesandfares/%s/%s/%s/%s/%s" % (fromSta, toSta, travelDate, travelTime, arriveDepart) # create the webscraping link
    # adds the return details if the user wants a return ticket
    if inReturn:
        URL += AddReturn(inRetDate, inRetTime, inRetArrive)
    soup = ScrapeWeb(URL) # get parsed webpage
    cheapestDetails, costString = GetCheapestFareDetailsFromWebpage(soup, inReturn) # get cheapest fare details and cost
    if inReturn:
        outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime = GetRequiredReturnFareDetails(cheapestDetails)
        return outFromSta, outToSta, outDepTime, outArrTime, costString, URL
        # return outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime, costString, URL
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
# fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL = FindTicket("norwich", "London", "tomorrow", "1200", True, False)
# print("\nYou will be travelling from %s (%s) to %s (%s), leaving at %s, and arriving at %s. The price will be %s" % (fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString))
# print("\n", URL)

# RETURN
# outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime, costString, URL = FindTicket("norwich", "London", "tomorrow", "1200", True, True, "21022021", "1200")
# print("You will be leaving from %s (%s) to %s (%s) at %s, and arriving at %s. Your return trip will be from %s (%s), to %s (%s) at %s, arriving at %s. The cost will be %s" % (outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime, costString))
# print("\n", URL)