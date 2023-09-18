import sqlite3
import json
import socket
import fcntl
import struct
import time
import requests
import unidecode
import re
import os
from urllib.parse import urlparse, unquote_plus, urlencode
from datetime import datetime
from crontab import CronTab
import sys
import urllib.request

app_path = os.path.dirname(os.path.realpath(__file__)) + "/"

url = "https://admin.indera.id/public/api/"

class GeneratorLen(object):
    def __init__(self, gen, length):
        self.gen = gen
        self.length = length

    def __len__(self): 
        return self.length

    def __iter__(self):
        return self.gen

def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
        )[20:24])
    except OSError:
        return 0

def getWlan():
    local_ip = get_ip_address('wlan0')
    if local_ip == 0:
        local_ip = get_ip_address('eth0')
    return local_ip


def getHandler(url):
    res = []
    try:
       res = requests.get(url,headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Safari/537.36'},timeout=7.0)
    except requests.ConnectionError as e:
        print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
        print(str(e))   
    except requests.Timeout as e:
        print("OOPS!! Timeout Error")
        print(str(e))
    except requests.RequestException as e:
        print("OOPS!! General Error")
        print(str(e))        
    return res

def postHandler(url,myobj):
    res = []
    try:
        res = requests.post(url,json=myobj,headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Safari/537.36'})
    except requests.ConnectionError as e:
        print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
        print(str(e))   
    except requests.Timeout as e:
        print("OOPS!! Timeout Error")
        print(str(e))
    except requests.RequestException as e:
        print("OOPS!! General Error")
        print(str(e))        
    return res
	
def getCctv():
    mresp = getHandler("http://admin.indera.id/public/api/ambil_cctv?owner=bjb&status=1&gen=1")
   # print(mresp.content)
    jresp = json.loads(mresp.content)
      
    return jresp
	
def cekUrl():
    resp = getCctv()
    cctvs = resp['data']
    for cctv in cctvs:
        print(urllib.request.urlopen('http://36.89.57.37/cctv/hls/'+cctv["name"]+'.m3u8').getcode())

def notExist(cron,line):
    if any(line in str(job) for job in cron):
        print("job exist")
        return False
    else:
        return True

def doCronUpdate(user):
    resp = getCctv()
    cctvs = resp['data']
    reslog = ''
    idx = 0
	
    with CronTab(user=user) as cron:
        if notExist(cron,str('* * * * * python3 /home/live/handler.py')):
            job = cron.new(command='python3 /home/live/handler.py')
            job.minute.every(1)
            #print('handler created')
            reslog += '\nhandler created'
	
    for cctv in cctvs:
        idx += 1
        reslog += '\n' +  str(idx) + ' ('  + str(datetime.now()) + ')'
        domain = urlparse(str(cctv["stream_server"])).netloc
        sourcesplit = urlparse(str(cctv["source"])).netloc.split('@')
        if(len(sourcesplit)==2):
            sourceip = sourcesplit[1]
        else:
            sourcesplit = ""
        
        #print('incoming * * * * * run-one /home/live/stream.sh ' + str(cctv["name"]) + ' ' + str(cctv["source"]) + ' ' + sourceip + ' PUNWAHYU ' + str(cctv["stream_server"])  + '  > /home/live/logs/' + str(cctv["name"]) + '.log 2>&1')
        reslog += '\nincoming * * * * * run-one /home/live/stream.sh ' + str(cctv["name"]) + ' ' + str(cctv["source"]) + ' ' + sourceip + ' ' + str(cctv["token"]) + ' ' + domain  + '  > /home/live/logs/' + str(cctv["name"]) + '.log 2>&1'
        name_iter = cron.find_command(str(cctv['name'])+'.log')
        list_iter = list(name_iter)
        len_iter = int(len(list_iter))
        if len_iter > 0:
            #print(len_iter)
            for item in list_iter:
                if str(item) == str('* * * * * run-one /home/live/stream.sh ' + cctv["name"] + ' ' + cctv["source"] + ' ' + sourceip + ' ' + str(cctv["token"]) + ' ' + domain  + '  > /home/live/logs/' + cctv["name"] + '.log 2>&1'):
                    #print('no change')
                    reslog += '\nno change'
                else:
                    #print('current : ' + str(item))
                    reslog += '\ncurrent : ' + str(item)
                    #rem_job = cron.find_command(str(cctv['name'])+'.log')
                        
                    with CronTab(user=user) as cron:
                        cron.remove(item)
                        job = cron.new(command='run-one /home/live/stream.sh ' + cctv["name"] + ' ' + cctv["source"] + ' ' + sourceip + ' ' + str(cctv["token"]) + ' ' + domain  + '  > /home/live/logs/' + cctv["name"] + '.log 2>&1')
                        job.minute.every(1)
                        #print('replaced')
                        reslog += '\nreplaced'
        else:
            with CronTab(user=user) as cron:
                splitname = cctv["name"].split("-")
                if(len(splitname)==1):
                    job = cron.new(command='run-one /home/live/stream.sh ' + cctv["name"] + ' ' + cctv["source"] + ' ' + sourceip + ' ' + str(cctv["token"]) + ' ' + domain  + '  > /home/live/logs/' + cctv["name"] + '.log 2>&1')
                    job.minute.every(1)
                    #print('created')
                    reslog += '\ncreated'
                else:
                    #print('skipped')
                    reslog += '\nskipped'
				
    with CronTab(user=user) as cron:
        for cr in cron:
            cronsplit = str(cr).split(' ')
            if(len(cronsplit)==16):
                result = next(
                    (cctv for cctv in cctvs if cctv["name"] == cronsplit[7]),
                    None
                )
                if(result==None):
                    reslog += '\n' + str(cronsplit[7]) + ' removed'
                    cron.remove(cr)
                else:
                    with open('/home/live/logs/'+result['name']+'.log', 'r') as f:
                        try:
                            log = str(datetime.now()) + '-' + f.readlines()[-1]
                            sendlog = getHandler("http://admin.indera.id/public/api/send_log?name="+result['name']+"&sensor="+log)
                        except:
                            sendlog = getHandler("http://admin.indera.id/public/api/send_log?name="+result['name']+"&sensor=None")
                    
        if notExist(cron,str('@hourly killall ffmpeg')):
            job = cron.new(command='killall ffmpeg')
            job.hour.every(1)
            #print('killer created')
            reslog += '\nkiller created'
            
    reslog += '\n'
    logFile = open('/home/live/logs/handler.log', 'w')
    print(reslog,file=logFile)
			
doCronUpdate('root')