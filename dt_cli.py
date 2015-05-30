import sys
from sys import stdin
import urllib2
import urllib
import socket

SERVER_OFFSET = 20000

server_addrs = ["127.0.0.1:30001","127.0.0.1:30002","127.0.0.1:30003","127.0.0.1:30004","127.0.0.1:30005","127.0.0.1:30006"]

def add_portval(addr, x=SERVER_OFFSET):
    ip,port = addr.split(':')
    return ip + ":" + str(int(port)+x)

def push_to_server(cmd, args, addr = server_addrs[0]):
    data = urllib.urlencode(args)
    for saddr in server_addrs:
        try:
            addr = add_portval(saddr)
            url = "http://" + addr + '/' + cmd + '?'
            response = urllib2.urlopen(url+data, timeout = 2)
            print "POST Request:" + url+data
            result = response.read()
            print "Response:" + result
            return result
        except:
            print "No response from ", saddr
            continue
def get_server_list(args):
    print server_addrs

def update_server_addrs(args):
    global server_addrs
    cmd = "getServersList"
    result = None
    for saddr in server_addrs:
        try:
            addr = add_portval(saddr)
            url = "http://" + addr + '/' + cmd
            print "POST. Request:" + url
            response = urllib2.urlopen(url, timeout = 2)
            result = response.read()
            if result is not None: break
        except:
            print "No response from ", saddr
            continue
    if result is not None:
        print "Response:" + result
        server_addrs = []
        for s in result.split(','):
            server_addrs.append(s[1:-1])
        print "updated: ", server_addrs

def get_key(args):
    key = args[0]
    push_to_server("get",{"key":key})

def set_key(args):
    key, val = args[0],args[1]
    push_to_server("set",{"key":key, "value":val})

def append(args):
    key, val = args[0],args[1]
    push_to_server("append",{"key":key, "value":val})

def lPush(args):
    key, val = args[0],args[1]
    push_to_server("lPush",{"key":key, "value":val})

def lPop(args):
    key = args[0]
    push_to_server("lPop",{"key":key})

def lIndex(args):
    key, val = args[0],args[1]
    push_to_server("lIndex",{"key":key, "index":val})

def strlen(args):
    key = args[0]
    push_to_server("getStrlen",{"key":key})

def llen(args):
    key = args[0]
    push_to_server("lLen",{"key":key})

def show_usage(args):
    print "List of cmds:"
    for i in sorted(CMD.keys()): print i
    print "type quit or q to exit"

CMD = {"get": get_key, "set":set_key, "append":append, "lpush":lPush,"lpop" :lPop, "lindex":lIndex, "strlen":strlen, "llen":llen, "up":update_server_addrs, "ss":get_server_list, "help":show_usage}


def process_cmd(usrcmd):
    # print "CMD: " + usrcmd

    usl = usrcmd.lower()
    if usl == 'q' or usl == 'exit':
        return True

    cmd = usl.split()[0].strip()
    if cmd in CMD:CMD[cmd](usrcmd.split()[1:])
    else: print "unrecognized cmd."

    return False

def say_hello():
    print "Hi, I'm DiminishedTriad, aka DT."
    print "Ready to try out the most awesome kv store ever? (type help for help)"

say_hello()
while True:
    sys.stdout.write('>> ')
    if process_cmd(stdin.readline().strip()):
        break



