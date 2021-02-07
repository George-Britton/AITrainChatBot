import datetime
import csv
import nltk 
# from datetime import datetime
import re
import TicketScrape
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize 
from time import strptime
#Importing modules
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
#Importing modules for prediction
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
from sklearn.model_selection import train_test_split
# path = 'C:/Users/ajd_r/Source/Repos/Ai Chatbot/response.txt'
# responses_file = open(path, 'r+')
chatbot = ChatBot('trainBot')
# trainer = ListTrainer(chatbot)

trainer = ChatterBotCorpusTrainer(chatbot)
# trainer.train("chatterbot.corpus.english")
trainer.train("chatterbot.corpus.english.greetings",
              "chatterbot.corpus.english.conversations")
book_list = []
for syn in wordnet.synsets("booking"): 
    for lemm in syn.lemmas(): 
        book_list.append(lemm.name())

cont_list = []
for syn in wordnet.synsets("contingency"): 
    for lemm in syn.lemmas(): 
        cont_list.append(lemm.name())

delay_list = []
for syn in wordnet.synsets("delay"): 
    for lemm in syn.lemmas(): 
        delay_list.append(lemm.name())

counter = 0
stvalid = False
stations = {"NRW" : "Norwich", "DIS" : "Diss", "SMK" : "Stowmarket", "IPS" : "Ipswich", "MNG" : "Manningtree", "COL" : "Colchester"}
data = pd.read_csv("Value set.csv")

X = data.iloc[:,[2]].values
y = data.iloc[:,[ 3]].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

stop_words = set(stopwords.words('english')) 
global booking, souc, dest, trdate, cntg_flag
booking = False
delay_f = False
cntg_flag = False
def getTag(txt):
    tokenized = sent_tokenize(txt) 
    for i in tokenized: 
        
        # Word tokenizers is used to find the words  
        # and punctuation in a string 
        wordsList = nltk.word_tokenize(i) 
    
        # removing stop words from wordList 
        wordsList = [w for w in wordsList if not w in stop_words]  
    
        #  Using a Tagger. Which is part-of-speech  
        # tagger or POS-tagger.  
        tagged = nltk.pos_tag(wordsList) 
    return tagged

def getName(txt):               #Getting Nouns
    tagged = getTag(txt)  

    if len(tagged) == 1:
        return tagged[0][0]

    for t in tagged:
        if 'NNP' in t:
            return(t[0])

def getNum(txt):                #Getting Numbers
    tagged = getTag(txt)  

    if len(tagged) == 1:
        return tagged[0][0]

    for t in tagged:
        if 'CD' in t:
            return(t[0])

def getResp(num,ucomm):        #Function to be called from UI to get response
    global booking, souc, dest, trdate, counter, cntg_flag, delay_f
# Get booking Syntaxes
    trbk = [ele for ele in book_list if(ele in ucomm)]
    if trbk or booking == True:
        booking = True
        
        res = getBooking(counter,ucomm)
        ret = res[0]
        URL = res[1]
        return ret, URL  
    
    dely = [ele for ele in delay_list if(ele in ucomm)]
    if dely or delay_f == True:
        delay_f = True
        res = getDelay(ucomm)
        ret = res[0]
        URL = res[1]
        return ret, URL 

        # res = getDelay(ucomm)

    cntg = [ele for ele in cont_list if(ele in ucomm)]
    if cntg or cntg_flag == True:
        cntg_flag = True
        res = getContingency(ucomm)
        # res = getBooking(counter,ucomm)
        ret = res[0]
        URL = res[1]
        return ret, URL
     
    ret = str(chatbot.get_response(ucomm))
    return ret, None

def getDelay(ucomm):
    global counter, delay_f, event, v1, v2, v3
    URL = ''
    if counter == 0:
        ret = 'Hi, my name is delayBot. Sorry to hear that your train has been delayed. Please let me know Station name you just arrived.'
        counter += 1
        return ret, None
    elif counter == 1:
        v1 = getName(ucomm)
        stvalid = validateStation(v1)
        if stvalid:
            ret = "And what is name of your destination station?"
            counter += 1
            return ret , URL
        else:
            ret = 'Please Enter a valid station name'
            return ret , URL
    elif counter == 2:
        v2 = getName(ucomm)
        stvalid = validateStation(v2)
        if stvalid:
            ret = "How many minutes has it been delayed?"
            counter += 1
            return ret , URL
        else:
            ret = 'Please Enter a valid station name'
            return ret , URL
    elif counter == 3:
        v3 = getNum(ucomm)
        v4 = float(v3)
        end_delay = getDelayedTime(v1,v2,v4)
        v5 = end_delay[0][0]
        v5 = int(v5)
        ret = (f"You will reach {v2}, {v5} minutes late")
        delay_f = False
        counter = 0
        ret = str(ret)
        return ret, URL

def getDelayedTime(v1,v2,v3):
    global stations, regressor
    feed = np.array([[v3]])
    co = 0
    pred = v3
    stations_inbet = 0
    for s in stations:
        if stations[s] == v1:
            co += 1
        if stations[s] == v2:
            stations_inbet = co
            co = 0
        if co >= 1:
            co += 1
    c2 = 0
    while c2 < stations_inbet:
        pred = regressor.predict(feed)
        feed[0][0] = pred
        c2 += 1
    
    return pred

def getContingency(ucomm):
    global counter, cntg_flag, event, v1, v2, v3, v4
    URL = ''
    roles = {"Instructions to Signallers/Controllers":2, "Operational Resources Required":3, "Critical Infrastructure":4, "Customer Service Staff Deployment":5, 
            "Alternative Transport":6, "Customer Message":7, "Internal Message to include":8, "Electronic Information (Whiteboard, website, social media)":9}
    v4 = 0
    if counter == 0:
        ret = 'Hi, my name is staffBot. I can help you dealing with contingencies. Please let me know Station name you just left.'
        counter += 1
        return ret, None
    elif counter == 1:
        # event = getName(ucomm)
        v1 = getName(ucomm)
        stvalid = validateStation(v1)
        if stvalid:
            ret = "And what is name of the next station?"
            counter += 1
            return ret , URL
        else:
            ret = 'Please Enter a valid station name'
            return ret , URL
    elif counter == 2:
        v2 = getName(ucomm)
        stvalid = validateStation(v2)
        if stvalid:
            ret = "What type of blockage are you facing?(Partial/Full)"
            counter += 1
            return ret , URL
        else:
            ret = 'Please Enter a valid station name'
            return ret , URL
    elif counter == 3:
        v3 = ""
        if "partial" in ucomm.lower():
            v3 = "Partial"
        elif "full" in ucomm.lower():
            v3 = "Full"
        else:
            ret = 'What type of blockage are you facing?(Partial/Full)'
            return ret , URL
        v3 = v3.title()
        ret = "What information do you need? Choose from below, either type in the number or type the full description as you see.\n"
        rl = str(roles)
        rl = rl.replace("," , "\n")
        ret = ret + rl
        counter += 1
        return ret , URL
    elif counter == 4:
        try:
            v4 = int(ucomm)
        except ValueError:
            v4 = roles[ucomm]
        v4 = int(v4)
        searc = (f"{v3} Line Blockage Between {v1} & {v2}")
        owing = v3 + " Line Blockage"
        txtnew = ""
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        with open('CM_chk.csv', 'rt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                Text = row[1]
                ResSearch = re.search(searc, Text)
                if ResSearch:
                    txtnew = row[v4]
                    txtnew = txtnew.replace("{xxx}" , owing)
                    txtnew = txtnew.replace("xxx" , owing)
                    txtnew = txtnew.replace("xx:xx", current_time)
        if txtnew == "":
            ret = "Could not find any contingency plan"
        else:
            ret = txtnew
        cntg_flag = False
        counter = 0
        return ret, URL

def validateStation(loc):
    if loc == 'London':
        return True
    with open("GB_stations.csv", 'rt') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
                if loc == row[0]: 
                    return True
    return False

def getBooking(num,ucomm):     #Function to handle booking related queries
    global booking, souc, dest, trdate, counter
    URL = ''
    if counter == 0:
        ret = 'Hi, my name is trainBot. I can help you with train booking. Please let me know your name first.'
        counter += 1
        return ret, None
    elif counter == 1:
        name = getName(ucomm)

        ret = "Hello "+name+", Where do you want to go?"
        counter += 1
        return ret , URL
    elif counter == 2:
        dest = getName(ucomm)
        stvalid = validateStation(dest)
        if stvalid:
            ret = "And where are you travelling from?"
            counter += 1
            return ret , URL
        else:
            ret = 'Please Enter a valid station name'
            return ret , URL
        
    elif counter == 3:
        souc = getName(ucomm)
        stvalid = validateStation(souc)
        if stvalid:
            ret = "When are you planning to travel?"
            counter += 1
            return ret , URL
        else:
            ret = 'Please Enter a valid station name'
            return ret , URL
    elif counter == 4:
        tom = []
        tod = []
        for syn in wordnet.synsets("tomorrow"): 
            for lemm in syn.lemmas(): 
                tom.append(lemm.name())
        tom_flag = [ele for ele in tom if(ele in ucomm.lower())]
        for syn in wordnet.synsets("today"): 
            for lemm in syn.lemmas(): 
                tod.append(lemm.name())
        tod_flag = [ele for ele in tod if(ele in ucomm.lower())]
        if tom_flag:
            trdate = datetime.datetime.today() + datetime.timedelta(days=1)
            trdate = str(trdate)
            trdate = trdate[0:10]
            trdate = trdate[8:] + '.' + trdate[5:7] + '.' + trdate[:4]
        elif tod_flag:
            trdate = datetime.datetime.today()
            trdate = str(trdate)
            trdate = trdate[0:10]
            trdate = trdate[8:] + '.' + trdate[5:7] + '.' + trdate[:4]
        else:
            date = getNum(ucomm)
            month_name = 'dummy'
            month_name = getName(ucomm)
            if month_name != 'dummy':
                month_number = strptime(month_name[:3], '%b').tm_mon
                if month_number < 10:
                    month_number = str(month_number)
                    month_number = '0' + month_number
                trdate = date[:2] + '.' + str(month_number) + '.' + '2020'
        ret = 'Do you want to check return tickets as well?'
        counter += 1
        return ret , URL
    elif counter == 5:
        if 'no' in ucomm:
            fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL = TicketScrape.FindTicket(souc,dest,trdate)
            ret = (f"You will be travelling from {fromStr} ({fromAbr}) to {toStr} ({toAbr}), leaving at {depTimeStr}, and arriving at {arrTimeStr}. The price will be {costString}")
            booking = False
            counter = 0
            return ret, URL
        elif 'yes' in ucomm:
            ret = 'Please let me know when do you want to return'
            counter += 1
            return ret , URL
    elif counter == 6:
        tom = []
        tod = []
        for syn in wordnet.synsets("tomorrow"): 
            for lemm in syn.lemmas(): 
                tom.append(lemm.name())
        for syn in wordnet.synsets("today"): 
            for lemm in syn.lemmas(): 
                tod.append(lemm.name())
        tom_flag = [ele for ele in tom if(ele in ucomm.lower())]
        tod_flag = [ele for ele in tod if(ele in ucomm.lower())]
        if tom_flag:
            rtdate = datetime.datetime.today() + datetime.timedelta(days=1)
            rtdate = str(trdate)
            rtdate = trdate[0:10]
            rtdate = trdate[8:] + '.' + trdate[5:7] + '.' + trdate[:4]
        elif tod_flag:
            rtdate = datetime.datetime.today()
            rtdate = str(trdate)
            rtdate = trdate[0:10]
            rtdate = trdate[8:] + '.' + trdate[5:7] + '.' + trdate[:4]
        else:
            date = getNum(ucomm)
            month_name = 'dummy'
            month_name = getName(ucomm)
            if month_name != 'dummy':
                month_number = strptime(month_name[:3], '%b').tm_mon
                if month_number < 10:
                    month_number = str(month_number)
                    month_number = '0' + month_number
                rtdate = date[:2] + '.' + str(month_number) + '.' + '2020'
        
        fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL = TicketScrape.FindTicket(souc,dest,trdate,True,rtdate)
        ret = (f"You will be travelling from {fromStr} ({fromAbr}) to {toStr} ({toAbr}), leaving at {depTimeStr}, and arriving at {arrTimeStr} and returning on {rtdate}. The price will be {costString}")
        booking = False
        counter = 0
        return ret, URL
