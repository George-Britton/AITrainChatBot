import datetime
import csv
import nltk 
import PyPDF2
import re
import TicketScrape
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize 
from time import strptime
#Importing modules
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
# path = 'C:/Users/ajd_r/Source/Repos/Ai Chatbot/response.txt'
# responses_file = open(path, 'r+')
chatbot = ChatBot('trainBot')
# trainer = ListTrainer(chatbot)

trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")
book_list = []
for syn in wordnet.synsets("booking"): 
    for lemm in syn.lemmas(): 
        book_list.append(lemm.name())

cont_list = []
for syn in wordnet.synsets("contingency"): 
    for lemm in syn.lemmas(): 
        cont_list.append(lemm.name())

counter = 0
stvalid = False

stop_words = set(stopwords.words('english')) 
global booking, souc, dest, trdate, cntg_flag
booking = False
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
    global booking, souc, dest, trdate, counter, cntg_flag
# Get booking Syntaxes
    trbk = [ele for ele in book_list if(ele in ucomm)]
    if trbk or booking == True:
        booking = True
        
        res = getBooking(counter,ucomm)
        ret = res[0]
        URL = res[1]
        return ret, URL  
    
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

def getContingency(ucomm):
    global counter, cntg_flag, event, v1, v2, v3
    URL = ''
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
        # searc = v3 + " Line Blockage Between " + v1 + " & " + v2
        searc = (f"{v3} Line Blockage Between {v1} & {v2}")
        pdf_file = open('D3_AICC_05 Contingency Plan Manual.pdf', 'rb')
        fileReader = PyPDF2.PdfFileReader(pdf_file)
        number_of_pages = fileReader.getNumPages()
        txtnew = ""
        for i in range(9, number_of_pages):
            PageObj = fileReader.getPage(i)
            Text = PageObj.extractText() 
            ResSearch = re.search(searc, Text)
            if ResSearch:
                txtnew = txtnew + Text.strip('\n')
                # print("this is page " + str(i)) 
                # print(Text)
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
            ret = "You will be travelling from %s (%s) to %s (%s), leaving at %s, and arriving at %s. The price will be %s" % (fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString)
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
        
        outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime, costString, URL = TicketScrape.FindTicket(souc,dest,trdate,True,rtdate)
        ret = "You will be leaving from %s (%s) to %s (%s) at %s, and arriving at %s. Your return trip will be from %s (%s), to %s (%s) at %s, arriving at %s. The cost will be %s" % (outFromSta, outFromStaAbr, outToSta, outToStaAbr, outDepTime, outArrTime, backFromSta, backFromStaAbr, backToSta, backToStaAbr, backDepTime, backArrTime, costString)
        booking = False
        counter = 0
        return ret, URL
