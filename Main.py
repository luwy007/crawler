#coding=utf-8
import Login
import GetPage
import time
import re
import random 
import queue
import Weibo
import webbrowser 
import os 
import json
import sys
from GetPage import LoadingTooFrequentException

def output(text):
    writer = open("E:\\result.txt","w")
    writer.write(text)
    writer.close()

def getPageNumber(idd, opener):
    global db  
    try: 
        #tryGetPage(idd,page,pagebar,opener)  why is pagebar here 3?? 
        text = GetPage.tryGetPage(idd, 1, 3, opener)
    except GetPage.NoMicroblogException:
        return 0
    
    
    #output(text)
    if text.find("微博列表") == -1:  
        return 1
    # # this should be repaired
    matches = re.search(r'&nbsp;(\d+)&nbsp;', text)   
    if matches is None:
        return 0  
    
    n = int(matches.group(1))
    
    return n

class TimeLimitException(Exception):pass

class TooManyMicro(Exception):pass

def getMicroblog(idd, pages, opener, MIDs,batch=20):    
    #global db
    global sleepTime
    global randomTimes
    result = True
    try:
        for i in range(1, pages + 1):
            micros = 0
            TEnd = time.time()
            TBegin = [0.0]
            for j in range(0, 3):    
                try:    
                    #in fact, i don't know the details of this function
                    text = GetPage.tryGetPage(idd, i, j, opener)        
                except GetPage.FailureOverTimesException as e:
                    print(e)
                    continue
                except GetPage.LoadingFailingException as e:
                    print(e)
                    continue
                except GetPage.NetworkBusyException as e:
                    print(e)
                    continue 
        
                microblogs = text.split("div action-type=\"feed_list_item\" ")
                micros += len(microblogs)
                if(len(microblogs)==1 and isLastOne(microblogs[0])):
                    raise TimeLimitException
                for microblog in microblogs:
                    if(not store(idd,microblog,MIDs,TBegin)):          #store() will return a judgement for the microblog's birthday, then go on or end up
                        raise TimeLimitException
                time.sleep(randomTimes * random.random() + sleepTime)
            if(i==1):
                TBegin[0] /= 1000 
                days = (TEnd-TBegin[0])/(3600*24)+0.1
                # if microblog density is bigger than 1.5/day, return false. that is mean the microblog's comments won't be crawled
                if((micros/days)>0.5):   
                    result = False
                    print("post too frequently")
                    break            
    finally:
        print("end grab microblog", idd)
        return result

def isLastOne(microblog):
    if(microblog.find("<!-- \/高级搜索 -->") and microblog.find("<!-- \/分页 --> ")):
        return True

def store(idd,microblog,MIDs,TBegin):
    #store mid, time, text in microblog into file
    #open
    file = open(path+str(idd)+"\\Microblog.txt","a",encoding='utf-8')
    #to find mid
    mid = ""
    if(microblog.find("mid")>=0):
        index = microblog.index("mid=\"")+5 
        mid = microblog[index:index+16]
        mid = trimMid(mid)
        if (mid is not None):
            MIDs.append(mid)
            file.write("[mid : "+mid+"]")
        else:
            return True
            print ("mid is none")
        
    else:
        #print("no microblog id info")
        return True
       
        
    #to find time
    time = ""
    if(microblog.find("feed_list_item_date\" date=\"")>=0):
        index = microblog.index("feed_list_item_date\" date=\"")+27
        time = microblog[index:index+13]
        TBegin[0] = int(time)
        file.write("[time : "+time+"]")
        if(not judgeTimeAfter(time)):           # if the microblog was born before 2013, grabbing will be ended
            return False    #MIDs = MIDs[:len(MIDs)-1]
    else:
        print("no time info")      
    
    self_text = ""
    #to find self weibo_text
    if(microblog.find("feed_list_content")>=0):
        microblog = microblog[microblog.index("feed_list_content"):]
        if(microblog.find("<\/div>")>0):
            weibo_text = microblog[microblog.index(">"):microblog.index("<\/div>")+1]
            while(weibo_text.find("<")>=0):
                index_head = weibo_text.index(">")
                index_tail = weibo_text.index("<")
                sub = weibo_text[index_head+1:index_tail]
                weibo_text = weibo_text[index_tail+1:]
                self_text += trim(sub)
            try:
                file.write("[self_text : "+self_text+"]")
            except Exception as e:
                file.write("[self_text :  ]")
               # print(e)        #delete this
                
        else:
            print("weibo_text has no tail <\/div>!")
        
    #to find others' weibo_text
    others_text = ""
    if(microblog.find("feed_list_reason")>=0):
        microblog = microblog[microblog.index("feed_list_reason"):]
        if(microblog.find("<\/div>")>0):
            weibo_text = microblog[microblog.index(">"):microblog.index("<\/div>")+1]
            while(weibo_text.find("<")>=0):
                index_head = weibo_text.index(">")
                index_tail = weibo_text.index("<")
                sub = weibo_text[index_head+1:index_tail]
                weibo_text = weibo_text[index_tail+1:]
                others_text += trim(sub)
            try:
                file.write("[others_text : "+others_text+"]")
            except Exception as e:
                file.write("[others_text :  ]")
               # print(e)
        else:
            print("weibo_text has no tail <\/div>!")
    
    file.write("\n")
    file.close()
    return  True

def trim(sub):
    while(sub.find("\n")>=0):
        sub = sub[:sub.index("\n")]+sub[sub.index("\n")+1:]
    while(sub.find("  ")>=0):
        sub = sub[:sub.index("  ")]+sub[sub.index("  ")+1:]
    while(sub.find("\t")>=0):
        sub = sub[:sub.index("\t")]+sub[sub.index("\t")+1:]
    if(len(sub)==1 and sub.find(" ")>=0):
        return ""
    return sub+" "

def grab(idd, openers,MIDs):
    global sleepTime
    global randomTimes
    
    for opener in openers: 
        delete = True
        result = False
        try:
            #n = getPageNumber(idd, opener)
            #if (n>40):          #too many microblogs 
             #   print(idd, n)
              #  print("no grabbing")
               # return
            #if n <= 0:
             #   pass
                #return
            #print(idd, n)
            result = getMicroblog(idd, 40, opener,MIDs)            
        except GetPage.IdNotExistException as e:
            pass
        except GetPage.AccountFrozenException as e:
            print(e)
            delete = False 
        except Exception as e:
            delete = False
            print(e)
        finally:        # attention!!! crawling may become too frequently
            '''if delete: 
                time.sleep(0.5) #time.sleep(randomTimes * random.random() + sleepTime)'''
            if (result):
                return True
            else:
                return False
        
def changeSleepTime():
    #it will sleep 900s, and sleeptime will be decreased by 0.1
    global sleepTime  
    while True:
        time.sleep(900)
        if sleepTime > 0.1:
            sleepTime -= 0.1
        print("sleepTime", sleepTime)
    
def changeRandomTimes():
    #it will sleep 3600s, and randomTimes will be decreased by 0.1
    global randomTimes
    while True:
        time.sleep(3600)
        if randomTimes > 0.1:
            randomTimes -= 0.1
        print("randomTimes", randomTimes)
 
def initOpeners():
    # store each opener in openersQueue
    global openersQueue
    global openers
    
    for o in openers:
        openersQueue.put(o)

def trimMid(mid):
    if(mid[len(mid)-1]<='9' and mid[len(mid)-1]>='0'):
        return mid
    else:
        length = len(mid)
        for i in range(length):
            if(mid[length-i-1]<='9' and mid[length-i-1]>='0'):
                return mid[:length-i]

def getComments(mid,access_token,expire_in):
    APP_KEY = ""
    APP_SECRET = ""
    CALL_BACK = ""
    
    client = Weibo.APIClient(APP_KEY, APP_SECRET, CALL_BACK)
    client.set_access_token(access_token, expire_in)
    comments = client.get.comments__show(id=mid)
    return comments

def getUserIdFromComments(comments,IdList,IDs_unsorted):
    # insert user id into IdList, and return count
    count = 0
    IDs = ExtractId(comments)
    for ID in IDs:
        new_inserted = insertIdIntoIdList(IdList, ID,IDs_unsorted)   #if id is inserted successfully, new_inserted=1
        count += new_inserted
    return count

def ExtractId(comments):
    IDs = []
    for i in range(len(comments)):
        ID = comments[i]["user"]["id"]
        IDs.append(ID)
    return IDs

def insertIdIntoIdList(IdList,ID,IDs_unsorted):         #insert algorithm has some problems
    place = findPlaceForNewId(IdList, ID)
    if(place==-1):
        return 0
    else:
        IdList.insert(place,ID)
        IDs_unsorted.append(ID)
        #IDs_to_be_review.write(str(ID)+"\n")
        return 1

def findPlaceForNewId(IdList,ID):
    # i don't this function's robustness
    if(len(IdList)==0):
        return 0
    head = 0
    tail = len(IdList)-1
    while(head<tail-1):
        if(ID==IdList[(head+tail)//2]):
            return -1
        elif(ID<IdList[(head+tail)//2]):
            tail = (head+tail)//2-1
        else:
            head = (head+tail)//2+1
    for index in range(head,tail+1):
        if (ID==IdList[index]):
            return -1
        if(ID<IdList[index]):
            return index
        elif(index == tail):
            return tail+1
            
def getAccessToken_ExpireIn():
    APP_KEY = ""
    APP_SECRET = ""
    CALL_BACK = ""
    client = Weibo.APIClient(APP_KEY, APP_SECRET, CALL_BACK)
    authorize_url = client.get_authorize_url(redirect_uri = CALL_BACK)
    webbrowser.open(authorize_url)
    code = input("input the code: ").strip()
    
    r = client.request_access_token(code,CALL_BACK)
    access_token = r.access_token  
    expires_in = r.expires_in
    return access_token,expires_in

def judgeTimeAfter(time):       #judge the microblog's birthday
    temp = float(time)
    T = 24*3600*365*1000
    year = temp/T+1970
    deadline = 2013
    if(year>deadline):
        return True
    else:
        return False
    
def getUserFans(user):         #get fans of the user
    fans = int(user["followers_count"])
    return fans

def setClients():
    access_tokens = []
    expire_in = 
    #access_token, expire_in = getAccessToken_ExpireIn()
    APP_KEY = []                    
    APP_SECRET = [] 
    CALL_BACK = ""
    clients = []
    for i in range(40):
        client = Weibo.APIClient(APP_KEY[i], APP_SECRET[i], CALL_BACK)
        client.set_access_token(access_tokens[i], expire_in)
        clients.append(client)
    
    return clients

def getClient(clients,index,seconds = 3600):#print("the %s is forbidden"%str(index))
    print("the %s is forbidden at %s"%(str(index),time.strftime("%H:%M:%S")))
    seconds = 10
    if(index==39):
        print("the %s is forbidden at %s"%(str(index),time.strftime("%H:%M:%S")))
        print("sleep for %ss"%str(seconds))
        time.sleep(seconds)
        print("sleep ending")
        return 0,clients[0]
    else:
        return index+1,clients[index+1]

def changeToInt(time):
    Months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    
    Mon = time[4:7]
    index = 0
    for index in range(len(Months)):
        if(Months[index]==Mon):
            break
    year = time[-4:]
    Unix_time = (int(year)-1970+float(index)/12)*365*24*3600*1000
    return Unix_time

def recognizeZombie(user):
    Created_time = changeToInt(user["created_at"])
    Unix_time_now = int(time.time())*1000
    using_time = (Unix_time_now-Created_time)/(24.0*3600*1000)
    statuses_count = user["statuses_count"]
    if(statuses_count/(using_time)>2):
        return True
    elif(user["friends_count"]>1000 and user["followers_count"]>0):
        if(user["friends_count"]/user["followers_count"]>3):
            return True
    elif(user["followers_count"]==0):
        return True
    else:
        return False

def recognizeVIP(user):
    if (user["followers_count"]>1500):
        return True
    else:
        return False

def recognizeTooYoung(user):
    Created_time = changeToInt(user["created_at"])
    Young_time = (2014-1970)*365*24*3600*1000
    if(Created_time>Young_time):
        return True
    else:
        return False

def main():
    IDs_sorted = [1868538694]  
    IDs_unsorted = [1868538694]
    cursor = 0
    ID = IDs_unsorted[0]
    global path
    global IDs_to_be_review
    try:
        GetCursor = open(path+"Cursor_Info.txt","r")
        line = GetCursor.readline().strip()
        cursor = int(line)
    except Exception as e:
        print(e)
    if(cursor>1):
        GetIDs = open(path+"IDs_to_be_review.txt","r")
        while(True):                 #change cycle module
            try:
                ID = int(GetIDs.readline())
                insertIdIntoIdList(IDs_sorted, ID, IDs_unsorted)            #IDs_to_be_review is too long
            except Exception as e:
                break
        GetIDs.close()
    #in debugging, following will pour out incomplete comments.txt and microblogs.txt
    ID = IDs_unsorted[cursor]
    try:
        os.makedirs(path+str(ID))
    except OSError as e:
        print(e)
    writer = open(path+str(ID)+"\\Comments.txt","w")
    writer.close()
    writer = open(path+str(ID)+"\\Microblog.txt","w")
    writer.close()
        
    clients = setClients()
    index = -1       # it can be selected randomly depended on needs
    index,client = getClient(clients,index)
    
    info = client.get.account__rate_limit_status()
    while(True):
        if(cursor<=len(IDs_unsorted)):
            try:
                ID = IDs_unsorted[cursor]
                cursor += 1 
                initLength = len(IDs_unsorted)
                MIDs = []
                BadRequest = False
                try:
                    os.makedirs(path+str(ID))
                except OSError as e:
                    print(e)
                Cursor_Info = open(path+"Cursor_Info.txt","w")          
                Cursor_Info.write(str(cursor))
                Cursor_Info.close()     
                try:
                    #grab() will return true if Micblog density is not too much, that means it's comments deserve crawled
                    if(not grab(ID,openers,MIDs)):  
                        continue     
                except LoadingTooFrequentException as e:
                    print(cursor)
                    print(e)
                except TooManyMicro as e:
                    continue
                '''
                while(True):
                    try:
                        user = client.get.users__show(uid = ID)
                        break
                    except Exception as e:
                        if(e.code==400):
                            BadRequest = True
                            break
                        #print(e)
                        info = client.get.account__rate_limit_status()
                        seconds = info["reset_time_in_seconds"]
                        index,client = getClient(clients,index,seconds)
                if (BadRequest):
                    continue
                if(recognizeVIP(user) or recognizeZombie(user)):
                    continue
                try:
                    grab(ID,openers,MIDs)           
                    count_total += 1
                    Cursor_Info = open(path+"Cursor_Info.txt","w")          
                    Cursor_Info.write(str(cursor))
                    Cursor_Info.close() 
                    # ending could be at this place        
                except LoadingTooFrequentException as e:
                    print(cursor)
                    print(e)
                if(recognizeTooYoung(user)):
                    continue
                '''       
                if(len(MIDs)>500):
                    continue
                
                writer = open(path+str(ID)+"\\Comments.txt","a",encoding='utf-8')
                anchor = 0             
                begin = len(IDs_unsorted) 
                overflow = False
                Cursor_Info = open(path+"Cursor_Info.txt","w")          
                Cursor_Info.write(str(cursor-1))
                Cursor_Info.close()
                for mid in MIDs:            
                    anchor += 1
                    while(True):
                        try:
                            comments = client.get.comments__show(id=mid)["comments"]
                            break
                        except Exception as e:
                            #print(e)
                            info = client.get.account__rate_limit_status()
                            #seconds = int(info["reset_time_in_seconds"])
                            index,client = getClient(clients,index,10)
                    getUserIdFromComments(comments, IDs_sorted,IDs_unsorted)        #efficiency is too low for the length of IDs_unsorted
                    if(len(IDs_unsorted)<(begin)+150):
                        writer.write("[mid : %s][comments : %s]\n"%(str(mid),json.dumps(comments,ensure_ascii=False))) 
                        writer.flush()
                    else:
                        writer.close()
                        writer = open(path+str(ID)+"\\Comments.txt","w")
                        writer.close()
                        overflow = True
                        break
                if(not overflow):
                    writer.close()
                    end = len(IDs_unsorted)
                    for i in range(begin,end):
                        IDs_to_be_review.write("\n"+str(IDs_unsorted[i]))           
                    IDs_to_be_review.flush()      
                else:
                    IDs_unsorted = IDs_unsorted[:begin]
                IDs_Info = open(path+"IDs_Info.txt","a")
                IDs_Info.write(str(ID)+" : "+str(len(IDs_unsorted)-initLength)+"\n")
                IDs_Info.close()
                Cursor_Info = open(path+"Cursor_Info.txt","w")          # this should be copied to the following except 
                Cursor_Info.write(str(cursor))
                Cursor_Info.close()
            except Exception as e:
                print(e)
        else:
            break
    IDs_to_be_review.close()

def test():
    clients = setClients()
    index = -1       # it can be selected randomly depended on needs
    index,client = getClient(clients,index)
    while(True):
        try:
            user = client.get.users__show(uid = 1620701264)
            changeToInt(user["created_at"])
            break
        except Exception as e:
            print(e)
            info = client.get.account__rate_limit_status()
            index,client = getClient(clients,index,10)

               
sleepTime = 1.2
randomTimes = 1.2
countForCallback = 0
path = "E:\\projects\\crawler\\microblogs\\"
try:
        os.makedirs(path)
except OSError as e:
        print(e)
IDs_to_be_review = open(path+"IDs_to_be_review.txt","a")

openersQueue = queue.Queue()
openers = Login.logins() 
initOpeners()
MIDs = []
#test()
#grab(,openers,MIDs)
main()
