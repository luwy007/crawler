#coding=gbk

import Login
import urllib
import time
import random


# #定义了一系列的异常！！！
class WrongUserOrPasswordException(Exception):
    def __init__(self, user, password):
        self.user = user
        self.password = password
        
    def __str__(self):
        return"用户名或密码错误！用户名 " + self.user + " 密码: " + self.password
    
class IdNotExistException(Exception):
    def __init__(self, idd):
        self.idd = idd
        
    def __str__(self):
        return "该账号不存在: " + str(self.idd)
    
class AccountFrozenException(Exception):
    def __init__(self, account):
        self.account = account
        
    def __str__(self):
        return "账号被冻结！id: " + str(self.account)
        
class FailureOverTimesException(Exception):
    def __init__(self, times, account, idd, page, pagebar):
        self.times = times
        self.account = account
        self.idd = idd
        self.page = page
        self.pagebar = pagebar
        
    def __str__(self):
        return "账号  " + self.account + " 爬取id为  " + str(self.idd) + \
            " 的第 " + str(self.page) + " 页第  " + str(self.pagebar) + " 分页时失败次数超过限制: " + str(self.times) + " 次"
    
class NoMicroblogException(Exception):
    def __init__(self, idd):
        self.idd = idd
        
    def __str__(self):
        return str(self.idd) + " 还没发过微博"
        
class LoginStatusLosingException(Exception):
    def __init__(self, account):
        self.account = account
        
    def __str__(self):
        return "账号 " + self.account + " 丢失登录状态"
    
class LoadingFailingException(Exception):
    def __init__(self, account, idd, page, pagebar):
        self.account = account
        self.idd = idd
        self.page = page
        self.pagebar = pagebar
        
    def __str__(self):
        return "账号  " + self.account + " 爬取id为  "\
            + str(self.idd) + " 的第  " + str(self.page) + " 页第  " + str(self.pagebar) + " 分页时加载失败"
            
class LoadingTooFrequentException(Exception):
    def __init__(self, account, idd, page, pagebar):
        self.account = account
        self.idd = idd
        self.page = page
        self.pagebar = pagebar
        
    def __str__(self):
        return "账号  " + self.account + " 爬取id为  "\
            + str(self.idd) + " 的第  " + str(self.page) + " 页第  " + str(self.pagebar) + " 分页时加载过于频繁"

class NetworkBusyException(Exception):
    def __init__(self, account, idd, page, pagebar):
        self.account = account
        self.idd = idd
        self.page = page
        self.pagebar = pagebar
        
    def __str__(self):
        return "账号  " + self.account + " 爬取id为  "\
            + str(self.idd) + " 的第  " + str(self.page) + " 页第  " + str(self.pagebar) + " 分页时被告知网络繁忙"
"""新浪自动加载的解决方案

body={'__rnd':访问这一页面的时间，以秒表示的13位整数
'_k':本次登录第一次访问此微薄的时间，16位整数
'_t':0
'count':第二次和第二次访问时都是15，第一次访问时是50
'end_id':最新的这一项微博的mid
'max_id':已经访问到的，也就是lazyload上面的这一项最旧的微博的mid
'page':要访问的页码
'pagebar':第二次是0，第三次是1，第一次没有这项
'pre_page':第二次和第三次都是本页页码，第一次访问是上页页码
'uid':博主的uid}
url='http://Weibo.com/aj/mblog/mbloglist?'+urllib.urlencode(body)"""
def getPage(idd, page, pagebar, opener):
    # what does 'body' mean???????
    body = {'__rnd':1343647638078,  # 这个是有抓包得出的，因为新浪微博用了瀑布流动态加载，所以不能一次性得到一页中所有信息
          '_k':1343647471134109,
          '_t':0,
          'count':15,
          'end_id':3473519214542343,
          'max_id':3473279479126179,
          'page':1,
          'pagebar':1,
          'pre_page':0,
          'uid':idd}
        
    body['page'] = page
   
    if pagebar == 0:
        body['count'] = '50'
        body['pagebar'] = ''
        body['pre_page'] = page - 1
    elif pagebar == 1:
        body['count'] = '15'
        body['pagebar'] = '0'
        body['pre_page'] = page
    elif pagebar == 2:
        body['count'] = '15'
        body['pagebar'] = '1'
        body['pre_page'] = page

    website = 'http://Weibo.com/aj/mblog/mbloglist?' + urllib.parse.urlencode(body)
   
    try:
        # result is a http.client.HTTPResponse object
        result = opener['opener'].open(website, timeout=30)
    except Exception as e:
        raise(e)
        
    try:       
        t = result.read()
        # # text is??   
        text = t.decode("utf-8", "replace")
        if text.find("抱歉，您当前访问的帐号异常，暂时无法访问。") != -1:
            raise IdNotExistException(idd)
        elif text.find("用户名或密码错误") != -1:
            raise WrongUserOrPasswordException(opener['user'], opener['pwd'])
        elif text.find("微博帐号解冻") != -1:
            raise AccountFrozenException(opener['user'])
        elif text.find("抱歉，网络繁忙") != -1:
            raise NetworkBusyException(opener['user'], idd, page, pagebar)
        
        text = t.decode("gbk", "replace")
        if text.find("正在登录 ...") != -1 or \
        text.find("http://Weibo.com/sso/login.php") != -1 or \
        text.find("http://login.sina.com.cn/") != -1 or \
        text.find("http://passport.Weibo.com/sso/wblogin") != -1 or \
        text.find("http://Weibo.com/aj/mblog/mbloglist") != -1 or \
        text.find("http://passport.Weibo.com/wbsso/login") != -1:
            raise LoginStatusLosingException(opener['user'])         
        
        text = t.decode("unicode-escape", "replace")
        if text.find("加载失败") != -1:  # 说明加载失败了
            raise LoadingFailingException(opener['user'], idd, page, pagebar)
        if text.find("加载过于频繁") != -1:
            raise LoadingTooFrequentException(opener['user'], idd, page, pagebar)
        if text.find("还没有发过微博") != -1:
            raise NoMicroblogException(idd)
        if text.find("WB_feed_type SW_fun S_line2") == -1:
            if text.find("微博列表") == -1:  # 当text.find("微博列表")!=-1时，说明该页没有微博
                print(t)
                raise Exception("未知情况")
        
        return text
    finally:
        result.close()

def tryGetPage(idd, page, pagebar, opener, times=5, callback=None):
    for count in range(0, times):
        try:
            # what the text will be
            text = getPage(idd, page, pagebar, opener)
            return text
        except (WrongUserOrPasswordException, LoginStatusLosingException) as e:
            reLogin(opener)
            print(e)
            if callback != None:
                callback(e)
            sleepForRandomTime(count)
            # raise e
        except (IdNotExistException, NoMicroblogException, AccountFrozenException, \
                LoadingFailingException, NetworkBusyException) as e:
            # 实验证明加载失败和提示网络繁忙后进行多次尝试是无效的，所以应该直接返回
            if callback != None:
                callback(e)
            raise e
        except (LoadingTooFrequentException) as e:
            print(e)
            if callback != None:
                callback(e)
            sleepForRandomTime(count)
        except Exception as e:
            if callback != None:
                callback(e)
            raise LoadingTooFrequentException
            print ('----------------------请稍后,正在进行第' + str(count + 1) + '次尝试-----------------------------')
            print(opener['user'], idd, page, pagebar, e)
            sleepForRandomTime(count)
            
    raise FailureOverTimesException(times, opener['user'], idd, page, pagebar)
 
def sleepForRandomTime(count):
    time.sleep(random.randint(1, 10) + count * random.randint(300, 500))

def reLogin(opener):
    # #delete used cookie
    Login.clearCookies(opener['cj'])
    Login.login(opener['user'], opener['pwd'], opener['opener'])
    