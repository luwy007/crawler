#coding=gbk
'''
Created on 2014-10-9

@author: Administrator
'''

import urllib.request, urllib.parse, urllib.error
import Weibo
import webbrowser  
APP_KEY = ""
APP_SECRET = ""
CALL_BACK = ""

client = Weibo.APIClient(APP_KEY, APP_SECRET, CALL_BACK)
authorize_url = client.get_authorize_url(redirect_uri = CALL_BACK)  
def GetCode(userid,passwd):
    APP_KEY = ""
    APP_SECRET = ""
    CALL_BACK = ""
    client = Weibo.APIClient(app_key = APP_KEY, app_secret=APP_SECRET, redirect_uri=CALL_BACK)
    referer_url = client.get_authorize_url()
    postdata = {
        "action": "login",
        "client_id": APP_KEY,
        "redirect_uri":CALL_BACK,
        "userId": userid,
        "passwd": passwd,
        }

    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0",
        "Referer":referer_url,
        "Connection":"keep-alive"
    }
    req  = urllib.request.Request(
        url = CALL_BACK,
        data = urllib.parse.urlencode(postdata),
        headers = headers
    )
    resp = urllib.request.urlopen(req)
    return resp.geturl()[-32:]

#auth_url = client.get_authorize_url()
#print(auth_url)

#打开浏览器，需手动找到地址栏中URL里的code字段   
#webbrowser.open(authorize_url)  
  
# 手动输入新浪返回的code  
#code = input("input the code: ").strip()  


#code = GetCode()
 

#r = client.request_access_token(code,CALL_BACK)
#access_token = r.access_token  
#expires_in = r.expires_in
client.set_access_token("", )

#json = client.comments.show.get(id = "3752163627203241")
print (client.get.comments__show(id=""))#.statuses.user_timeline.get())
print ("good luck")


