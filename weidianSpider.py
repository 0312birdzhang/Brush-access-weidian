#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2017年1月21日

@author: debo.zhang
@requires: mechanize
@requires: bs4
'''
import mechanize
import json
from bs4 import BeautifulSoup
import multiprocessing
import time,random
import sys,os

USER_ID = "894049717"
UA_LIST = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
            "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Mobile Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
            "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; Maxthon/3.0)"
           ]
# Module multiprocessing is organized differently in Python 3.4+
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen
    


class NoHistory(object): 
    def add(self, *a, **k): pass 
    def clear(self): pass 

def worker(itemid):
    br = getBrowers()
    time.sleep(random.randint(3, 6))
    try:
        itemout = br.open("https://weidian.com/item.html?itemID="+itemid)
        itemout.read()
    except Exception as e:
        print(e)
    return


def getBrowers():
    br = mechanize.Browser(history=NoHistory())
    #options
    br.set_handle_equiv(True)
    #br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    
    #br.set_proxies({"http": "joe:password@myproxy.example.com:3128",
    #            "ftp": "proxy.example.com",
    #            })
    #br.add_proxy_password("joe", "password")
    
    #Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.set_debug_http(False)
    br.set_debug_redirects(False)
    br.set_debug_responses(False)
    br.addheaders = [("User-agent",UA_LIST[random.randint(0,len(UA_LIST)-1)])]
    return br


def getItems(html):
    soup = BeautifulSoup(html,"html5lib")
    script = soup.findAll('script')[-1].string
    data = script.split("var customTemplateInfo =")[1].split("var topListData")[0].rsplit(';', 1)[0]
    data = json.loads(data)
    return data

def getShops():
    #Browser
    br = getBrowers()
    try:
        r = br.open("http://weidian.com/?userid="+USER_ID)
        html = r.read()
        data = getItems(html)
        pool = multiprocessing.Pool(processes = (4 if multiprocessing.cpu_count() < 4 else multiprocessing.cpu_count()))
        for i in data.get("result").get("template_Info")[3].get("proxy_linkinfo"):
            if i.get("is_delete") != "0":
                continue
            itemid = i.get("itemID")
            pool.apply_async(worker, (itemid, ))
        pool.close()
        pool.join()
    except Exception as e:
        print(e)
    
if __name__ == "__main__":
    multiprocessing.freeze_support()
    while True:
        print(time.strftime('%Y-%m-%d %X', time.gmtime( time.time() ) ))
        print("Start visit My Bear's WeiShop...")
        getShops()
        sleep_time = random.randint(35,60)
        print("Let's watting "+str(sleep_time)+" seconds...")
        print("")
        print("")
        time.sleep(sleep_time)