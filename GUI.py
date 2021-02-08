#Creating GUI with tkinter
import tkinter
from tkinter import *
import time
import NLP_Check
import webbrowser
from tkHyperlinkManager import HyperlinkManager

#counter = 0
url = None

def send():
    #global counter
    global url
    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)
    
    if msg != '':
            ChatLog.config(state=NORMAL)
            ChatLog.insert(END, "You: " + msg)
            ChatLog.insert(END, '\n' + time.ctime() + '\n\n')
            #ChatLog.config(foreground="#442265", font=("Verdana", 12 ))
            ChatLog.see("end")
            #print(counter)
            
            res = NLP_Check.getResp(msg)
            if res[1] == None:
                ChatLog.insert(END, "Bot: " + res[0]+ '\n' + time.ctime() + '\n\n')
                print('a')
            else:
                url = str(res[1])
                ChatLog.insert(END, "Bot: " + res[0] + '\n')
                ChatLog.insert(END, res[1], hyperlink.add(clickme))
                ChatLog.insert(END, '\n' + time.ctime() + '\n\n')
                print('b')
            #counter = counter + 1
            
            ChatLog.config(state=DISABLED)
            ChatLog.yview(END)

def clickme():
    global url
    webbrowser.open_new(url)


base = Tk()
base.title("Train Help Bot")
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)

#Create Chat window
ChatLog = Text(base, bd=0, bg="white", fg="#442265", height="8", width="50", font=("Verdana", 12), wrap="word")

#ChatLog.pack()
ChatLog.insert('1.1', 'Welcome to the Train-Services Chat-Bot, I can help you with services like train ticket booking and train delay estimation. How may I help you today?\n' + time.ctime() + '\n\n')

ChatLog.config(state=DISABLED)

hyperlink = HyperlinkManager(ChatLog)




#Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="arrow")
ChatLog['yscrollcommand'] = scrollbar.set

#Create Button to send message
SendButton = Button(base, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b",fg='#ffffff',
                    command= send )

#Create the box to enter message
EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="Arial")
#EntryBox.bind("<Return>", send)


#Place all components on the screen
scrollbar.place(x=376,y=6, height=386)
ChatLog.place(x=6,y=6, height=386, width=370)
EntryBox.place(x=128, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=90)

#ChatLog.insert('2.2', 'This is a Text widget demo')

base.mainloop()
