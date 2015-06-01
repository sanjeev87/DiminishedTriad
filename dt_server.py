
# coding: utf-8

# In[1]:

import logging
from os import environ
logging.basicConfig(level=logging.DEBUG)
from spyne.application import Application
from spyne.decorator import srpc
from spyne.service import ServiceBase
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode
from spyne.model.complex import Iterable
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
import threading
import hashlib
import redis
import sys

class DiminishedTriadService(ServiceBase):

    def __init__(self):
        print "I am being instantiated !!!!"
        
    @srpc(Unicode, _returns=Unicode)
    def get(key):
        backs = getNextNBackends(key)
        #r = redis.StrictRedis(host='localhost', port=30001, db=0)
        print "lenght of backs : ", len(backs)
        print "backs : ", backs
        print "global map in get():", hash_to_back_map
        for back in backs:
            addr = back.split(":")[0]
            port = back.split(":")[1]
            try:
                #r = redis.StrictRedis(host=addr, port=port, db=0)
                r = getRedisPyInstance(back)
                return r.get(key)
            except:
                print "failed to get key: ", key ," from addr: ",addr," port: ", port
                continue
            
    @srpc(Unicode,Unicode, _returns=Unicode)
    def set(key,value):
        #r = redis.StrictRedis(host='localhost', port=30001, db=0)
        backs = getNextNBackends(key)
        print "setting key :", key, " to value :", value
        print "lenght of backs : ", len(backs)
        print "backs : ", backs
        print "global map in set():", hash_to_back_map
        for back in backs:
            addr = back.split(":")[0]
            port = back.split(":")[1]
            try:
#                 r = redis.StrictRedis(host=addr, port=port, db=0)
                r = getRedisPyInstance(back)
                r.set(key,value)
            except:
                print "failed to set key: ", key ," to addr: ",addr," port: ", port
                continue
        return OK
    
    @srpc(Unicode, _returns=Unicode)
    def update_hash_to_back_map(addrs):
        try:
            lock.acquire()
            new_hash_to_back_map = {}
            for addr in addrs.split(","):
                new_hash_to_back_map[hash(addr)] = addr
            hash_to_back_map.clear()
            for k in new_hash_to_back_map:
                hash_to_back_map[k] = new_hash_to_back_map[k]
        except:
            e = sys.exc_info()[0]
            print e
            return e
        finally:
            lock.release()
            return OK
    
    
    @srpc(_returns=Unicode)
    def getAOFLog():
        f = open(AOFPATH,'r')
        string = f.read()
        print "getAOF returning ", string
        return string
    
    @srpc(_returns=Unicode)
    def getServersList():
        s = str(hash_to_back_map.values())[1:-1]
        print "get server list:", s
        return s
    
    @srpc(Unicode,_returns=Integer)
    def getStrlen(key):
        backs = getNextNBackends(key)
        for back in backs:
            try:
                addr = back.split(":")[0]
                port = back.split(":")[1]
                #r = redis.StrictRedis(host=addr, port=port, db=0)
                r = getRedisPyInstance(back)
                return r.get(key)
            except:
                continue
                
    @srpc(Unicode,Unicode, _returns=Integer)
    def append(key,value):
        backs = getNextNBackends(key)
        for back in backs:
            try:
                addr = back.split(":")[0]
                port = back.split(":")[1]
#                 r = redis.StrictRedis(host=addr, port=port, db=0)
                r = getRedisPyInstance(back)
                return r.append(key,value)
            except:
                print "failed to append to key: ", key ," append_str : ", value ," to addr: ", addr , "port: " , port
                continue
        
    @srpc(Unicode,Unicode, _returns=Integer)
    def lPush(key,value):
        backs = getNextNBackends(key)
        for back in backs:
            try:
                addr = back.split(":")[0]
                port = back.split(":")[1]
#                 r = redis.StrictRedis(host=addr, port=port, db=0)
                r = getRedisPyInstance(back)
#                 print "calling lpush with key:", key , " append_str:", value
#                 print "pushing to addr:", addr, " port:", port
                return r.lpush(key,value)
            except:
                print "failed to lPush to key: ", key ," append_str : ", value ," to addr: ", addr , "port: " , port
                continue
                
    @srpc(Unicode, _returns=Integer)
    def lPop(key):
        backs = getNextNBackends(key)
        for back in backs:
            try:
                addr = back.split(":")[0]
                port = back.split(":")[1]
#                 r = redis.StrictRedis(host=addr, port=port, db=0)
                r = getRedisPyInstance(back)
                return r.lpop(key)
            except:
                print "failed to lPop to key: ", key ," to addr: ", addr , "port: " , port
                continue
    
    #from the list with key "key" get the element at index "index"      
    @srpc(Unicode,Integer, _returns=Unicode)
    def lIndex(key,index):
        backs = getNextNBackends(key)
        #r = redis.StrictRedis(host='localhost', port=30001, db=0)
#         print "lenght of backs : ", len(backs)
#         print "backs : ", backs
#         print "global map in l():", hash_to_back_map

        print "calling lIndex with key:", key, " index:", index
        print "type of index : ",  type(index)
        for back in backs:
            addr = back.split(":")[0]
            port = back.split(":")[1]
            try:
#                 r = redis.StrictRedis(host=addr, port=port, db=0)
                r = getRedisPyInstance(back)
                print "lindex is returning :", r.lindex(key,index)
                return r.lindex(key,index)
            except:
                print "failed to get index:", index ," key: ", key ," from addr: ",addr," port: ", port
                continue
    
    #from the list with key "key" get the length of the list   
    @srpc(Unicode, _returns=Integer)
    def lLen(key):
        backs = getNextNBackends(key)
        #r = redis.StrictRedis(host='localhost', port=30001, db=0)
#         print "lenght of backs : ", len(backs)
#         print "backs : ", backs
#         print "global map in l():", hash_to_back_map
        for back in backs:
            addr = back.split(":")[0]
            port = back.split(":")[1]
            try:
#                 r = redis.StrictRedis(host=addr, port=port, db=0)
                r = getRedisPyInstance(back)
                return r.llen(key)
            except:
                print "failed to get length of list with key :", key ,"from addr: ",addr," port: ", port
                continue
    
    
############################### End of Class DiminishedTriadService ########################################

NUMBACKENDS = 100 # this determines what we are modding by
NUMBACKUPS = 2
OK = "ok"

def hash(key):
    return int(hashlib.sha1(key).hexdigest(), 16)

lock = threading.RLock()
HOST = "127.0.0.1"
REDIS_PORT = 30002
AOFPATH = "create-multiredis/appendonly-" + str(REDIS_PORT) + ".aof"
hash_to_back_map = {
                            hash("127.0.0.1:30001"):"127.0.0.1:30001",
                            hash("127.0.0.1:30002"):"127.0.0.1:30002",
                            hash("127.0.0.1:30003"):"127.0.0.1:30003",
                            hash("127.0.0.1:30004"):"127.0.0.1:30004",
                            hash("127.0.0.1:30005"):"127.0.0.1:30005",
                            hash("127.0.0.1:30006"):"127.0.0.1:30006"
                    }

back_to_redis_map = {
                            "127.0.0.1:30001":redis.StrictRedis(host="127.0.0.1", port=30001, db=0)
                    }

def updateAOFPATH():
    AOFPATH = "create-multiredis/appendonly-" + str(REDIS_PORT) + ".aof"

def getNextNBackends(key):
    try:
        lock.acquire()
        keys = hash_to_back_map.keys()
        print "keys : ", keys
        keys.append(hash(key))
        keys = sorted(keys)
        index = keys.index(hash(key))
        out = []
        for i in range(1,NUMBACKUPS+2):
            # the master will be the (index + 1)th element 
            # we are selecting N+1 elements starting with the master -- master + N backups
            if keys[(index + i)%len(keys)] in hash_to_back_map and hash_to_back_map[keys[(index + i)%len(keys)]] not in out:
                out.append(hash_to_back_map[keys[(index + i)%len(keys)]])
        print "getNextNBackends for key : ",key," returning : {",out,"}"
        return out
    finally:
        lock.release()

def getRedisPyInstance(back):
    if back in back_to_redis_map:
        return back_to_redis_map[back]
    else:
        print "ERROR : trying to get redis py instance for backend :",back
        addr = back.split(":")[0]
        port = back.split(":")[1]
        back_to_redis_map[back] = redis.StrictRedis(host=addr, port=port, db=0)
        return back_to_redis_map[back]
        

def main():
    host = sys.argv[1]
    port = (int)(sys.argv[2])
#    host = "127.0.0.1"
#    port = 50001
    HOST = host
    REDIS_PORT = port - 20000
    updateAOFPATH()
    
    from wsgiref.simple_server import make_server
#     logging.basicConfig(level=logging.DEBUG)
#     logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
    application = Application([DiminishedTriadService],
        tns='DiminishedTriadService',
        in_protocol=HttpRpc(validator='soft'),
        out_protocol=JsonDocument()
    )
    wsgi_app = WsgiApplication(application)
    server = make_server(host, port, wsgi_app)
    server.serve_forever()
    

if __name__ == '__main__':
    main()
    
    
    


# In[ ]:




# In[ ]:



