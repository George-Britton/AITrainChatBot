import datetime
import nltk 
import TicketScrape
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize 
from time import strptime
path = 'C:/Users/ajd_r/Source/Repos/Ai Chatbot/response.txt'
responses_file = open(path, 'r+')
stop_words = set(stopwords.words('english')) 
global booking, souc, dest, trdate
booking = False
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
    global booking, souc, dest, trdate
# Get booking Syntaxes
    book_list = []
    for syn in wordnet.synsets("booking"): 
        for lemm in syn.lemmas(): 
            book_list.append(lemm.name())

    trbk = [ele for ele in book_list if(ele in ucomm)]
    if trbk or booking == True:
        booking = True
        res = getBooking(num,ucomm)
        ret = res[0]
        URL = res[1]
        return ret, URL

def getBooking(num,ucomm):     #Function to handle booking related queries
    global booking, souc, dest, trdate
    URL = ''
    if num == 0:
        ret = 'Hi, my name is trainBot. I can help you with train booking. Please let me know your name first.'
        return ret, None
    elif num == 1:
        name = getName(ucomm)

        ret = "Hello "+name+", Where do you want to go?"
        return ret , URL
    elif num == 2:
        dest = getName(ucomm)
        ret = "And where are you travelling from?"
        return ret , URL
    elif num == 3:
        souc = getName(ucomm)
        ret = 'When are you planning to travel?'
        return ret , URL
    elif num == 4:
        tom = []
        for syn in wordnet.synsets("tomorrow"): 
            for lemm in syn.lemmas(): 
                tom.append(lemm.name())
        tom_flag = [ele for ele in tom if(ele in ucomm)]
        if tom_flag:
            trdate = datetime.datetime.today() + datetime.timedelta(days=1)
            trdate = str(trdate)
            trdate = trdate[0:10]
            trdate = trdate[8:] + '.' + trdate[5:7] + '.' + trdate[:4]
        else:
            date = getNum(ucomm)
            month_name = 'dummy'
            month_name = getName(ucomm)
            if month_name != 'dummy':
                month_number = strptime(month_name, '%b').tm_mon
                if month_number < 10:
                    month_number = str(month_number)
                    month_number = '0' + month_number
                trdate = date + '.' + str(month_number) + '.' + '2020'
        ret = 'Do you want to check return tickets as well?'
        return ret , URL
    elif num == 5:
        if 'no' in ucomm:
            fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL = TicketScrape.FindTicket(souc,dest,trdate)
            ret = "You will be travelling from %s (%s) to %s (%s), leaving at %s, and arriving at %s. The price will be %s" % (fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString)
            booking = False
            return ret, URL






# s0 = input("I can help you with train booking or delay prediction. Please tell me what do you need?")

# trbk = [ele for ele in book_list if(ele in s0)]
# if trbk:
#     s1 = input("Hi, my name is trainBot. I can help you with train booking. Please let me know your name first.\n")
#     name = getName(s1)
#     s2 = input("Hello "+name+", Where do you want to go?\n")
#     dest = getName(s2)
#     s3 = input("And where are you travelling from?\n")
#     souc = getName(s3)
#     s4 = input("When are you planning to travel?\n")
#     tom = []
#     for syn in wordnet.synsets("tomorrow"): 
#         for lemm in syn.lemmas(): 
#             tom.append(lemm.name())
#     tom_flag = [ele for ele in tom if(ele in s4)]
#     if tom_flag:
#         trdate = datetime.datetime.today() + datetime.timedelta(days=1)
#         trdate = str(trdate)
#         trdate = trdate[0:10]
#         trdate = trdate[8:] + '.' + trdate[5:7] + '.' + trdate[:4]
#     else:
#         date = getNum(s4)
#         month_name = 'dummy'
#         month_name = getName(s4)
#         if month_name != 'dummy':
#             month_number = strptime(month_name, '%b').tm_mon
#             if month_number < 10:
#                 month_number = str(month_number)
#                 month_number = '0' + month_number
#             trdate = date + '.' + str(month_number) + '.' + '2020'
#     s5 = input("Do you want to check return tickets as well?")
#     if 'yes' in s5:
#         s6 = input("Please tell me the return date")
#         tom_flag = [ele for ele in tom if(ele in s4)]
#         if tom_flag:
#             rtdate = datetime.datetime.today() + datetime.timedelta(days=1)
#             rtdate = str(trdate)
#             rtdate = trdate[0:10]
#             rtdate = trdate[8:] + '.' + trdate[5:7] + '.' + trdate[:4]
#         else:
#             date = getNum(s4)
#             month_name = 'dummy'
#             month_name = getName(s4)
#             if month_name != 'dummy':
#                 month_number = strptime(month_name, '%b').tm_mon
#                 if month_number < 10:
#                     month_number = str(month_number)
#                     month_number = '0' + month_number
#                 rtdate = date + '.' + str(month_number) + '.' + '2020'
                
#     print(trdate)
#     print(dest)
#     print(souc)

#     fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL = TicketScrape.FindTicket(souc,dest,trdate)
    # print("\nYou will be travelling from %s (%s) to %s (%s), leaving at %s, and arriving at %s. The price will be %s" % (fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString))
#     print("\n", URL)
