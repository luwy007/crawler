#coding=gbk

import Login
import urllib
import time
import random


# #������һϵ�е��쳣������
class WrongUserOrPasswordException(Exception):
    def __init__(self, user, password):
        self.user = user
        self.password = password
        
    def __str__(self):
        return"�û�������������û��� " + self.user + " ����: " + self.password
    
class IdNotExistException(Exception):
    def __init__(self, idd):
        self.idd = idd
        
    def __str__(self):
        return "���˺Ų�����: " + str(self.idd)
    
class AccountFrozenException(Exception):
    def __init__(self, account):
        self.account = account
        
    def __str__(self):
        return "�˺ű����ᣡid: " + str(self.account)
        
class FailureOverTimesException(Exception):
    def __init__(self, times, account, idd, page, pagebar):
        self.times = times
        self.account = account
        self.idd = idd
        self.page = page
        self.pagebar = pagebar
        
    def __str__(self):
        return "�˺�  " + self.account + " ��ȡidΪ  " + str(self.idd) + \
            " �ĵ� " + str(self.page) + " ҳ��  " + str(self.pagebar) + " ��ҳʱʧ�ܴ�����������: " + str(self.times) + " ��"
    
class NoMicroblogException(Exception):
    def __init__(self, idd):
        self.idd = idd
        
    def __str__(self):
        return str(self.idd) + " ��û����΢��"
        
class LoginStatusLosingException(Exception):
    def __init__(self, account):
        self.account = account
        
    def __str__(self):
        return "�˺� " + self.account + " ��ʧ��¼״̬"
    
class LoadingFailingException(Exception):
    def __init__(self, account, idd, page, pagebar):
        self.account = account
        self.idd = idd
        self.page = page
        self.pagebar = pagebar
        
    def __str__(self):
        return "�˺�  " + self.account + " ��ȡidΪ  "\
            + str(self.idd) + " �ĵ�  " + str(self.page) + " ҳ��  " + str(self.pagebar) + " ��ҳʱ����ʧ��"
            
class LoadingTooFrequentException(Exception):
    def __init__(self, account, idd, page, pagebar):
        self.account = account
        self.idd = idd
        self.page = page
        self.pagebar = pagebar
        
    def __str__(self):
        return "�˺�  " + self.account + " ��ȡidΪ  "\
            + str(self.idd) + " �ĵ�  " + str(self.page) + " ҳ��  " + str(self.pagebar) + " ��ҳʱ���ع���Ƶ��"

class NetworkBusyException(Exception):
    def __init__(self, account, idd, page, pagebar):
        self.account = account
        self.idd = idd
        self.page = page
        self.pagebar = pagebar
        
    def __str__(self):
        return "�˺�  " + self.account + " ��ȡidΪ  "\
            + str(self.idd) + " �ĵ�  " + str(self.page) + " ҳ��  " + str(self.pagebar) + " ��ҳʱ����֪���緱æ"
"""�����Զ����صĽ������

body={'__rnd':������һҳ���ʱ�䣬�����ʾ��13λ����
'_k':���ε�¼��һ�η��ʴ�΢����ʱ�䣬16λ����
'_t':0
'count':�ڶ��κ͵ڶ��η���ʱ����15����һ�η���ʱ��50
'end_id':���µ���һ��΢����mid
'max_id':�Ѿ����ʵ��ģ�Ҳ����lazyload�������һ����ɵ�΢����mid
'page':Ҫ���ʵ�ҳ��
'pagebar':�ڶ�����0����������1����һ��û������
'pre_page':�ڶ��κ͵����ζ��Ǳ�ҳҳ�룬��һ�η�������ҳҳ��
'uid':������uid}
url='http://Weibo.com/aj/mblog/mbloglist?'+urllib.urlencode(body)"""
def getPage(idd, page, pagebar, opener):
    # what does 'body' mean???????
    body = {'__rnd':1343647638078,  # �������ץ���ó��ģ���Ϊ����΢�������ٲ�����̬���أ����Բ���һ���Եõ�һҳ��������Ϣ
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
        if text.find("��Ǹ������ǰ���ʵ��ʺ��쳣����ʱ�޷����ʡ�") != -1:
            raise IdNotExistException(idd)
        elif text.find("�û������������") != -1:
            raise WrongUserOrPasswordException(opener['user'], opener['pwd'])
        elif text.find("΢���ʺŽⶳ") != -1:
            raise AccountFrozenException(opener['user'])
        elif text.find("��Ǹ�����緱æ") != -1:
            raise NetworkBusyException(opener['user'], idd, page, pagebar)
        
        text = t.decode("gbk", "replace")
        if text.find("���ڵ�¼ ...") != -1 or \
        text.find("http://Weibo.com/sso/login.php") != -1 or \
        text.find("http://login.sina.com.cn/") != -1 or \
        text.find("http://passport.Weibo.com/sso/wblogin") != -1 or \
        text.find("http://Weibo.com/aj/mblog/mbloglist") != -1 or \
        text.find("http://passport.Weibo.com/wbsso/login") != -1:
            raise LoginStatusLosingException(opener['user'])         
        
        text = t.decode("unicode-escape", "replace")
        if text.find("����ʧ��") != -1:  # ˵������ʧ����
            raise LoadingFailingException(opener['user'], idd, page, pagebar)
        if text.find("���ع���Ƶ��") != -1:
            raise LoadingTooFrequentException(opener['user'], idd, page, pagebar)
        if text.find("��û�з���΢��") != -1:
            raise NoMicroblogException(idd)
        if text.find("WB_feed_type SW_fun S_line2") == -1:
            if text.find("΢���б�") == -1:  # ��text.find("΢���б�")!=-1ʱ��˵����ҳû��΢��
                print(t)
                raise Exception("δ֪���")
        
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
            # ʵ��֤������ʧ�ܺ���ʾ���緱æ����ж�γ�������Ч�ģ�����Ӧ��ֱ�ӷ���
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
            print ('----------------------���Ժ�,���ڽ��е�' + str(count + 1) + '�γ���-----------------------------')
            print(opener['user'], idd, page, pagebar, e)
            sleepForRandomTime(count)
            
    raise FailureOverTimesException(times, opener['user'], idd, page, pagebar)
 
def sleepForRandomTime(count):
    time.sleep(random.randint(1, 10) + count * random.randint(300, 500))

def reLogin(opener):
    # #delete used cookie
    Login.clearCookies(opener['cj'])
    Login.login(opener['user'], opener['pwd'], opener['opener'])
    