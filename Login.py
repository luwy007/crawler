#coding=utf-8
import binascii
import urllib
import http.cookiejar
import base64
import re
import json
import rsa

def get_servertime():

    url = 
    data = urllib.request.urlopen(url).read()
    p = re.compile('\\((.*)\\)')
    try:
        json_data = p.search(data.decode('utf-8')).group(1)
        data = json.loads(json_data)
        servertime = str(data['servertime'])
        nonce = data['nonce']
        rsakv = data['rsakv']
        pubkey = data['pubkey']
        return servertime, nonce, rsakv, pubkey
    except:
        print ('Get severtime error!')
        return None

def get_pwd(pwd, servertime, nonce, pubkey):    
    rsaPublickey = int(pubkey, 16)  
    key = rsa.PublicKey(rsaPublickey, 65537)  
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)  
    passwd = rsa.encrypt(message.encode(), key)    
    passwd = binascii.b2a_hex(passwd)  
    return passwd

def get_user(username):
    username_ = urllib.request.quote(username)
    username = base64.encodestring(username_.encode())[:-1]
    return username

def login(user, pwd, opener): 
    postdata = {
        'entry': 'weibo', 'gateway': '1', 'from': '', 'savestate': '7', 'userticket': '1', 'ssosimplelogin': '1',
        'vsnf': '1', 'vsnval': '', 'su': '', 'service': 'miniblog', 'servertime': '', 'nonce': '',
        'pwencode': 'rsa2', 'prelt':'115', 'rsakv':'', 'sp': '', 'encoding': 'UTF-8',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
    }
    
    url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.2)'
    try:
        servertime, nonce, rsakv, pubkey = get_servertime()  
    except:
        return
    
    postdata['servertime'] = servertime
    postdata['nonce'] = nonce
    postdata['rsakv'] = rsakv
    postdata['su'] = get_user(user)
    postdata['sp'] = get_pwd(pwd, servertime, nonce, pubkey)
    postdata = urllib.parse.urlencode(postdata)
    headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0;Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.3)'}
    req = urllib.request.Request(
        url=url,
        data=postdata.encode(),
        headers=headers
    )
    try:
        try:
            result = opener.open(req, timeout=30)
            text = result.read().decode("gbk")
        finally:
            result.close()
        
        p = re.compile('location\.replace\(\'(.*?)\'\)')
        login_url = p.search(text).group(1)
        
        try:
            result = opener.open(login_url, timeout=30)
        finally:
            result.close()
            
        print ("login success")
        return True
    except Exception as e:
        print ('Login error!', e)
        print("the ID %s is frozen now"%user)
        return False

def logins():
    users = []  
    
    pwd = ''
    returns = []
    
    for user in users:
        cj = http.cookiejar.LWPCookieJar()
        cookie_support = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
        
        if login(user, pwd, opener):
            result = {}
            result['opener'] = opener
            result['cj'] = cj
            result['user'] = user
            result['pwd'] = pwd
            returns.append(result)
     
    return returns  # 
        
def clearCookies(cj):
    cj.clear_expired_cookies()
    cj.clear_session_cookies()
    