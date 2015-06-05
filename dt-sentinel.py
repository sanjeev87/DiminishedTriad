
# coding: utf-8

# In[ ]:

import redis
import hiredis
from redis.sentinel import Sentinel
import urllib2
import urllib
import Queue
import hashlib
import threading
import time
import csv


# In[ ]:

def startSentinelListner():
    p = REDIS_SENTINEL.pubsub()
    channels = ['+sdown','-sdown']
    p.psubscribe('*')

    for message in p.listen():
        handleMessage(message)

# In[ ]:

REDIS_SENTINEL = None
MSG_QUEUE = None
NUMBACKUPS = int(open('NUM_BACKUPS.txt').readline())
HASH_TO_BACK_MAP = None
LOG_FILE = None
LOG_WRITER = None
FLAG_MASTER_JOIN = "migrate_master_join"
FLAG_JOIN = "join"
FLAG_LEAVE = "leave"


def dtSentinelInit():
    global REDIS_SENTINEL
    global MSG_QUEUE
    global HASH_TO_BACK_MAP
    global LOG_FILE
    global LOG_WRITER
    REDIS_SENTINEL = redis.StrictRedis(host='localhost', port=40001)
    # print REDIS_SENTINEL.sentinel_masters().keys()
    HASH_TO_BACK_MAP = {}
    updateHashToBackMap()
    # print REDIS_SENTINEL.sentinel_masters()
    print HASH_TO_BACK_MAP.values()
    MSG_QUEUE = Queue.Queue(maxsize=50)
    LOG_FILE = open(getLogFileName(), 'w')
    LOG_WRITER = csv.writer(LOG_FILE, delimiter=',')
    LOG_WRITER.writerow(['From', 'To', 'NumKeys', 'Keys', 'Flags'])


    
def getKeysInMaster(back):
    addr = back.split(":")[0]
    port = back.split(":")[1]
    r = redis.StrictRedis(host=addr, port=port, db=0)
    return r.keys("*")
    
def getKeysInRange(source_addr,addr1,addr2):    
    # copy keys in range from addr1+1 till addr2 from source_addr
    k1, k2 = hash(addr1), hash(addr2)
    keys_source_addr = getKeysInMaster(source_addr)
    out = []
    for key in keys_source_addr:
        if k2 > k1: # not crossing the beginning of ring
            if hash(key) > k1 and hash(key) <= k2:
                out.append(key)
        else:
            if hash(key) > k1 or (hash(key) >= 0 and hash(key) <= k2):
                out.append(key)
    return out
                
def migrateKeys(source_addr,destination_addr,keys,flag="none"):
    old_log = getMasterLogs(source_addr)
    new_log = ""
    log_diff = [""]
    addr = source_addr.split(":")[0]
    port = source_addr.split(":")[1]
    src_r = redis.StrictRedis(host=addr, port=port, db=0)
    dst_r = redis.StrictRedis(host=destination_addr.split(":")[0], port=destination_addr.split(":")[1], db=0)
    keyCount = 0
    keyList = ''
    while len(log_diff)>0:
        for key in keys:
            try:
                print "Dumping key: %s" % key
                value = src_r.dump(key)
                print "deleting from destination key:",key
                dst_r.delete(key)
                print "Restoring key: %s" % key
                dst_r.restore(key, 0, value)
                keyCount += 1
                keyList += key + ':'
            except Exception,e:
                print "Exception 5:",e
                print "UNable to migrate key:",key," from addr:",source_addr," to addr:", destination_addr
                continue
        new_log = getMasterLogs(source_addr)
        log_diff = getLogIncrementalCommands(old_log, new_log)
        old_log = new_log
        new_keys = []
        for i in log_diff:
            new_keys.append(i[1])
        keys = new_keys
    
    # writeLog(source_addr, destination_addr, keyCount, keyList,flag)
    writeLog(source_addr, destination_addr, keyCount,flag)
    return


def getMastersSorted():
    keys = sorted(HASH_TO_BACK_MAP.keys())
    
def hash(key):
    return int(hashlib.sha1(key).hexdigest(), 16)

def updateHashToBackMap():
    ml = getMastersList()
    HASH_TO_BACK_MAP.clear()
    for m in ml:
        HASH_TO_BACK_MAP[hash(m)] = m 
    print "HASH_TO_BACK_MAP updated, sorted values:", sorted(HASH_TO_BACK_MAP.values())
    print "HASH_TO_BACK_MAP updated, MAP :", HASH_TO_BACK_MAP

def getNextNBackends(server_addr, N=NUMBACKUPS):
    key = hash(server_addr)
    keys = sorted(HASH_TO_BACK_MAP.keys())
    index = keys.index(key)
    out = []
#     for k in keys:
#         print k, HASH_TO_BACK_MAP[k]
#     print "hash:", key, ":",server_addr
#     print "index:", index
    for i in range(1,N+1):
        # we are selecting N backends starting with the backend following the server_addr
        # the output list does not contain server_addr
        if keys[(index + i)%len(keys)] in HASH_TO_BACK_MAP and HASH_TO_BACK_MAP[keys[(index + i)%len(keys)]] not in out:
            out.append(HASH_TO_BACK_MAP[keys[(index + i)%len(keys)]])
    print "getNextNBackends for addr : ",server_addr," returning : {",out,"}"
    return out

def getPrevNBackends(server_addr, N=NUMBACKUPS):
    key = hash(server_addr)
    keys = sorted(HASH_TO_BACK_MAP.keys())
    print "trying to fins index of key:",key, " in hash to back map"
    index = keys.index(key)
    out = []
    for i in range(1,N+1):
        # we are selecting N backends starting with the backend preceeding the server_addr
        # the output list does not contain server_addr
        if keys[(index - i)%len(keys)] in HASH_TO_BACK_MAP and HASH_TO_BACK_MAP[keys[(index - i)%len(keys)]] not in out:
            out.append(HASH_TO_BACK_MAP[keys[(index - i)%len(keys)]])
    print "getPrevNBackends for addr : ",server_addr," returning : {",out,"}"
    return out

def getMastersList():
    return [REDIS_SENTINEL.sentinel_masters()[m]['ip'] + ':' + str(REDIS_SENTINEL.sentinel_masters()[m]['port']) for m in REDIS_SENTINEL.sentinel_masters() if not REDIS_SENTINEL.sentinel_masters()[m]['is_sdown']]

def sendMasterList(ml = HASH_TO_BACK_MAP.values() if HASH_TO_BACK_MAP else None):
    for url in ml:
        ip,port = url.split(':')
        sendListAsPost('http://'+ip+':'+str(int(port) + 20000), ml)

def handleJoin(msg):
    arr = msg['data'].split(" ")
    new_server_add = arr[2]
    new_server_port = arr[3]
    print "migrating data into new server : ", arr
    updateHashToBackMap()
    hashMapKeys = sorted(HASH_TO_BACK_MAP.keys())
    print "ring sequence"
    for k in hashMapKeys:
        print "addr:",HASH_TO_BACK_MAP[k] 
    new_server = new_server_add+":"+new_server_port
    #get the backend immediately ahead of the node that has joined
    next_N = getNextNBackends(new_server,1)
    next_back = next_N[0]
    
    # list to keep track of all our threads
    thread_list = []
    
    #get NUMBACKS + 1 nodes that are immediately behind the node that has just joined
    #the prev_backs list is anti clockwise in our ring !!! 
    prev_backs = getPrevNBackends(new_server,NUMBACKUPS+1)
    print " prev_backs of new server:",new_server, " is ", prev_backs
    
    for i in range(len(prev_backs)-1):
        try:
    #       keys = getKeysInRange(source_addr,addr1,addr2)
            keys = getKeysInRange(prev_backs[i],prev_backs[i+1],prev_backs[i])
            print "obtaining keys:",keys," between :",prev_backs[i+1] , " and ", prev_backs[i]
    #       migrateKeys(source_addr,destination_addr,keys)
            # t = threading.Thread(target=migrateKeys, args=(prev_backs[i],new_server,keys))
            t = threading.Thread(target=migrateKeys, args=(prev_backs[i],new_server,keys,FLAG_JOIN))
            # Sticks the thread in a list so that it remains accessible
            thread_list.append(t)
            #migrateKeys(prev_backs[i],new_server,keys)
            print "migrating keys:",keys," between :",prev_backs[i] , " and ", new_server
        except Exception,e:
            print "UNable to migrate from addr:",prev_backs[i]," to addr:", new_server
            print "Exception:1",e
            continue
        
    try:
        keys = getKeysInRange(next_back,prev_backs[0],new_server)
        print "In handle join getting keys between prev:",prev_backs[0], " and new server:", new_server
        # t = threading.Thread(target=migrateKeys, args=(next_back,new_server,keys))
        t = threading.Thread(target=migrateKeys, args=(next_back,new_server,keys,FLAG_MASTER_JOIN))
        # Sticks the thread in a list so that it remains accessible
        thread_list.append(t)
#         migrateKeys(next_back,new_server,keys)
        print "migrating keys:",keys," between :",next_back , " and ", new_server
    except Exception,e:
            print "UNable to migrate from addr:",next_back," to addr:", new_server
            print "Exception:10",e
            
    # Starts threads
    for thread in thread_list:
        thread.start()

    # block until all threads terminate
    for thread in thread_list:
        thread.join()
    
    sendMasterList(HASH_TO_BACK_MAP.values())
        
        
    
def handleLeave(msg):
    print 'handleLeave():'#, msg['data']
    dead_server_host = msg['data'].split(" ")[-2]
    dead_server_port = msg['data'].split(" ")[-1]
    dead_server = dead_server_host + ":" + dead_server_port
    backs_clockwise = getNextNBackends(dead_server, NUMBACKUPS + 1)
    backs_anticlockwise = getPrevNBackends(dead_server, NUMBACKUPS + 1)
    print backs_clockwise
    print backs_anticlockwise
    backs_anticlockwise_len = len(backs_anticlockwise)
    print backs_anticlockwise_len
    if len(backs_clockwise) != backs_anticlockwise_len:
        print "Error: lengths of previous and next backends do not match"
        return
    for i in range(0, backs_anticlockwise_len-1):
        keys = getKeysInRange(backs_anticlockwise[i], backs_anticlockwise[i+1], backs_anticlockwise[i])
        print keys
        migrateKeys(backs_anticlockwise[i], backs_clockwise[backs_anticlockwise_len - 2 - i], keys,FLAG_LEAVE)
        
    if backs_anticlockwise_len > 1:
        keys = getKeysInRange(backs_clockwise[0], backs_anticlockwise[0], dead_server)
        print keys
        migrateKeys(backs_clockwise[0], backs_clockwise[backs_anticlockwise_len - 1], keys,FLAG_LEAVE)
    
    updateHashToBackMap()
    sendMasterList(HASH_TO_BACK_MAP.values())
    
def handleMessage(message):
    #parseMasterLogs()
    t = message['channel']
    print message['data'], t
    if t == '+sdown':
        handleLeave(message)
    elif t == '-sdown' or t == '+monitor':
        handleJoin(message)
    else:
#         print "Unknown channel message:", message
        t = None
def sendListAsPost(url, slist):
    try:
        url = url + '/update_hash_to_back_map?'
        print url, slist
        s = ''
        for i in slist: s = s + ',' + i
        s = s[1:]
        data = urllib.urlencode({'addrs' : s})
    #     print 'encoded data', data
        print "Trying to POST Request:" + url+data
        response = urllib2.urlopen(url+data)
        
        result = response.read()
        return result
    except:
        print "Failed to update:",url
        return ""
    
def sanitizeString(resp):
    resp = resp.replace('\"', '')
    resp = resp.replace('\\n', '\n')
    resp = resp.replace('\\r', '\r')
    return resp
    
def getLogIncrementalCommands(previous_log, new_log):
    previous_log = sanitizeString(previous_log)
    new_log = sanitizeString(new_log)
    resp = new_log.replace(previous_log, "")
    try:
        reader = hiredis.Reader()
        resp = resp.replace('\"', '')
        resp = resp.replace('\\n', '\n')
        resp = resp.replace('\\r', '\r')
        reader.feed(resp)
        log_list = []
        l = reader.gets()
        while l!=False:
            log_list.append(l)
            print l
            l = reader.gets()
        return log_list
    except Exception, e:
        print e
        return []
        
def getMasterLogs(address):
    print "Getting logs for :", address
    try:
        url = '/getAOFLog'
        port = str((int)(address.split(':')[1])+20000)
        req = 'http://'+address.split(':')[0]+':'+port
        print req+url
        response = urllib2.urlopen(req+url)
        return str(response.read())
    except Exception, e:
        print e
        return ""
    
def getLogFileName():
    n = time.localtime()
    return  "DTS_log_"+ str(n.tm_mon) +"_"+ str(n.tm_mday) + "_" + str(n.tm_hour)+"_"+str(n.tm_min)+"_"+str(n.tm_sec) 


def writeLog(*args):
    l = []
    for a in args: l.append(a)
    # print "writing to log:", l
    print LOG_WRITER
    LOG_WRITER.writerow(l)
    LOG_FILE.flush()
    

dtSentinelInit()
startSentinelListner()

# In[ ]:




# In[ ]:




# In[ ]:



