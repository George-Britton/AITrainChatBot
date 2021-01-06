import datetime
import nltk 
import TicketScrape
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize 
from time import strptime
stop_words = set(stopwords.words('english')) 

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

def getName(txt):
    tagged = getTag(txt)  

    if len(tagged) == 1:
        return tagged[0][0]

    for t in tagged:
        if 'NNP' in t:
            return(t[0])

def getNum(txt):
    tagged = getTag(txt)  

    if len(tagged) == 1:
        return tagged[0][0]

    for t in tagged:
        if 'CD' in t:
            return(t[0])


book_list = []
for syn in wordnet.synsets("booking"): 
    for lemm in syn.lemmas(): 
        book_list.append(lemm.name())

s0 = input("I can help you with train booking or delay prediction. Please tell me what do you need?")

trbk = [ele for ele in book_list if(ele in s0)]
if trbk:
    s1 = input("Hi, my name is trainBot. I can help you with train booking. Please let me know your name first.\n")
    name = getName(s1)
    s2 = input("Hello "+name+", Where do you want to go?\n")
    dest = getName(s2)
    s3 = input("And where are you travelling from?\n")
    souc = getName(s3)
    s4 = input("When are you planning to travel?\n")
    tom = []
    for syn in wordnet.synsets("tomorrow"): 
        for lemm in syn.lemmas(): 
            tom.append(lemm.name())
    tom_flag = [ele for ele in tom if(ele in s4)]
    if tom_flag:
        trdate = datetime.datetime.today() + datetime.timedelta(days=1)
        trdate = str(trdate)
        trdate = trdate[0:10]
        trdate = trdate[8:] + '.' + trdate[5:7] + '.' + trdate[:4]
    else:
        date = getNum(s4)
        month_name = 'dummy'
        month_name = getName(s4)
        if month_name != 'dummy':
            month_number = strptime(month_name, '%b').tm_mon
            if month_number < 10:
                month_number = str(month_number)
                month_number = '0' + month_number
            trdate = date + '.' + str(month_number) + '.' + '2020'
    s5 = input("Do you want to check return tickets as well?")
    if 'yes' in s5:
        s6 = input("Please tell me the return date")
        tom_flag = [ele for ele in tom if(ele in s4)]
        if tom_flag:
            rtdate = datetime.datetime.today() + datetime.timedelta(days=1)
            rtdate = str(trdate)
            rtdate = trdate[0:10]
            rtdate = trdate[8:] + '.' + trdate[5:7] + '.' + trdate[:4]
        else:
            date = getNum(s4)
            month_name = 'dummy'
            month_name = getName(s4)
            if month_name != 'dummy':
                month_number = strptime(month_name, '%b').tm_mon
                if month_number < 10:
                    month_number = str(month_number)
                    month_number = '0' + month_number
                rtdate = date + '.' + str(month_number) + '.' + '2020'
                
    print(trdate)
    print(dest)
    print(souc)

    fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString, URL = TicketScrape.FindTicket(souc,dest,trdate)
    print("\nYou will be travelling from %s (%s) to %s (%s), leaving at %s, and arriving at %s. The price will be %s" % (fromStr, fromAbr, toStr, toAbr, depTimeStr, arrTimeStr, costString))
    print("\n", URL)
