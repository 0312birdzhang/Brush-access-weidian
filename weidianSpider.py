#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2017年1月21日

@author: debo.zhang
'''
import mechanize
import json
from bs4 import BeautifulSoup
import multiprocessing
import time,random
import sys,os

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
    

USER_ID = "894049717"

class NoHistory(object): 
    def add(self, *a, **k): pass 
    def clear(self): pass 

def worker(itemid):
    br = getBrowers()
    time.sleep(random.randint(3, 6))
    itemout = br.open("https://weidian.com/item.html?itemID="+itemid)
    itemout.read()
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
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    return br


def getItems(html):
    soup = BeautifulSoup(html,"html.parser")
    script = soup.findAll('script')[-1].string
    data = script.split("var customTemplateInfo =")[1].split("var topListData")[0].rsplit(';', 1)[0]
    data = json.loads(data)
    return data

def getShops():
    #Browser
    br = getBrowers()
    r = br.open("http://weidian.com/?userid="+USER_ID)
    html = r.read()
    data = getItems(html)
    pool = multiprocessing.Pool(processes = 8)
    for i in data.get("result").get("template_Info")[3].get("proxy_linkinfo"):
        if i.get("is_delete") != "0":
            continue
        itemid = i.get("itemID")
        pool.apply_async(worker, (itemid, ))
    pool.close()
    pool.join()
    
if __name__ == "__main__":
    multiprocessing.freeze_support()
    while True:
        print time.strftime('%Y-%m-%d %X', time.gmtime( time.time() ) )
        print "Start visit My Bear's WeiShop..."
        getShops()
        sleep_time = random.randint(35,60)
        print "Let's watting "+str(sleep_time)+" seconds..."
        print ""
        print ""
        time.sleep(sleep_time)