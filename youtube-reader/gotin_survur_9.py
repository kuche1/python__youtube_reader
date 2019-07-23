
#9

#o
import sys
import traceback
from threading import Thread,Lock
import socket
from time import time,sleep
from urllib.parse import unquote_plus as unquote

#c

#l
argv = sys.argv
nil = None

######################################$3     SETTINGS     E$######################################

TARGET_FILE = 'youtube_new_user_connection.py'#has to end in .py

BIND_IP = ''   #
BIND_PORT = 3333   #http://www.abc.de:80 | http://www.abc.de
BIND_WAITLIST_MAXLEN = 5   #max active people waiting for connection [and not being disconnected]

MAX_ACCEPT_THR = 5   #at most X users can connect at a time
ACCEPT_THR_NO_NEW_INSTANCE_DELAY = 0.4   #time for a nap if no new instances were needed

DATA_RECV_TIME = 16   #maximum time for reciving a full request
DATA_RECV_NO_NEW_BIT_DELAY = 0   #if no new bit is recived, wait that long

######################################$3   END SETTINGS   E$######################################







#con.py

to_del_all_pref = ['/'] #more complex first: ['==>','==','=']

def clean_once(url,mcharset):
    for charset in mcharset:
        if url.startswith(charset):
            return url[url.index(charset):]

def commonize_url(url):
    while 1:
        r = clean_once(url,to_del_all_pref)
        if r:
            url = r
        else:
            break
    return url

class Con():
    def __init__(s,con,meth,url,proto):
        s.con = con
        s.meth = meth
        s.url = commonize_url(url)
        print(f'new url: {s.url}')
        s.proto = proto
    def recv(s,am):
        return s.con.recv(am)
    def sendb(s,data):
        s.con.setblocking(True)
        try:
            return s.con.sendall(data)
        except ConnectionAbortedError:
            return 'connection-aborted'
        finally:
            s.con.setblocking(False)
    def close(s):
        return s.con.close()

    def sendstr(s,data):
        return s.sendb(data.encode('utf-8'))
    def send(s,data):
        return s.sendstr(str(data))
    def sendfile(s,d):
        f = open(d,'rb')
        data = f.read()
        f.close()
        return s.sendb(data)










#END IMPORT


_print = print
print_lock = Lock()
def print(*ar,**kw):
    print_lock.acquire()
    _print(*ar,*kw)
    print_lock.release()



def sendlsterr(con,file='[No data]'):
    exc_type,exc_value,exc_tb = sys.exc_info()
    res = traceback.format_exception(exc_type,exc_value,exc_tb)
    #res.reverse()

    resp = ''
    resp += f'Error in file: {file}\n'
    for line in res:
        resp += line

    try:
        con.sendstr(resp)
    except ConnectionResetError:
        print('couldnt send error report')

    



class Thread_regulator():
    def __init__(s,fnc,maxinstances,*args,**kwargs):
        s.DELAY = ACCEPT_THR_NO_NEW_INSTANCE_DELAY
        
        s.fnc = fnc
        s.maxinstances = maxinstances
        s.args = args
        s.kwargs = kwargs

    def thr(s):
        try:
            s.fnc(*s.args,**s.kwargs)
        finally:
            s.running_instances -= 1
            print(f'Ending thread number [+=?]: {s.running_instances}')
    
    def __call__(s):
        s.running_instances = 0
        while Running:
            if s.maxinstances > s.running_instances:
                s.running_instances += 1
                print(f'Starting thread number [+=?]: {s.running_instances}')
                Thread(target=s.thr).start()
            else:
                sleep(s.DELAY)




def accept_new_connection():
    try:
        print('Waiting for connection')
        con,addr = sock.accept()
    except OSError:
        print('::Exiting thread by internal request...')
        return
    ip = addr[0]
    con.setblocking(False)

    lastbits = [b'']*4
    all_data = b''
    end = time() + DATA_RECV_TIME
    while end > time():
        try:
            bit = con.recv(1)
        except BlockingIOError:
            sleep(DATA_RECV_NO_NEW_BIT_DELAY)
        else:
            if bit==b'':
                break
            all_data += lastbits.pop(0)
            lastbits += [bit]
            if lastbits == [b'\r',b'\n',b'\r',b'\n']:
                break
    else:
        print('Closing incomplete request')
        return con.close()


    
    info = all_data.decode('utf-8')
    info = info.split('\r\n')


    header = info.pop(0)
    header = header.split(' ')
    if len(header) != 3:
        print(f'Header: {header}')
        header = ['err','err','err']
    for ind,i in enumerate(header):
        header[ind] = unquote(i)
    meth,url,proto = header
    

    body = {}
    for line in info:
        if ': ' in line:
            ind = line.index(': ')
            name = line[:ind]
            value = line[ind+2:]
            body[name] = value

    con = Con(con,meth,url,proto)

    try:
        f = open(TARGET_FILE,'rb')
    except FileNotFoundError:
        err = f'File doesnt exist: {TARGET_FILE}'
        print(err)
        con.send(err)
        con.close()
    else:
        commands = f.read()
        f.close()
        
    
    try:
        imported_module = {}
        imported_module['print'] = print
        exec(commands,imported_module)
    except:
        err = f'Error while compiling file: {TARGET_FILE}'
        print(err)
        con.send(f'Error while compiling file: {TARGET_FILE}')#... maxtime for con.send()
        con.close()
        raise

    if 'main' not in imported_module:
        err = f'ERROR: File has no main function: {TARGET_FILE}'
        print(err)
        con.send(err)
        return con.close()
        
    try:
        imported_module['main'](con)
    except Exception as err:
        con.send(f'Exception: {err}')
        con.close()
        raise
    
    return con.close()
    


print(f'binding socket to port: {BIND_PORT}')
sock = socket.socket()
try:
    while 1:
        try: sock.bind((BIND_IP,BIND_PORT))
        except OSError: sleep(0.2)
        else: break
except KeyboardInterrupt:
    print('Exiting...')
    sys.exit()
sock.listen(BIND_WAITLIST_MAXLEN)
print('socket bound')


Running = 1


accept_thread_regulator = Thread_regulator(accept_new_connection,MAX_ACCEPT_THR)
Thread(target=accept_thread_regulator).start()


try:
    while 1:
        sleep(60)
except KeyboardInterrupt:
    print('Ending Program...')
finally:
    Running = 0
    sock.close()
    print('Port unbinded')





















