import socket
import json
import pickle
import sys,os
import time

def c_print(*args):
    print('[CLIENT]',*args)

from resp import response

class client:

  def __init__(self, url, port=1234, HEADERSIZE = 10):
    self.port = port
    self.url = url
    self.HEADERSIZE = HEADERSIZE
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def recieve_page(self):
    out = b""
    new = True
    leng = 0
    print('Captured:')
    while True:
      msg = self.s.recv(8)

      if new:
        leng = msg.decode("utf-8").replace('"','').strip()
        leng = int(leng[:self.HEADERSIZE])
        print('Header:',leng)
        new = False

      out += msg
      sys.stdout.write('\r'+str(len(out)-self.HEADERSIZE)+' out of '+str(leng))
      sys.stdout.flush() 
      if len(out)-self.HEADERSIZE == leng or len(out)-self.HEADERSIZE == leng+4:
        print('\nDone!')
        out = out[self.HEADERSIZE:]
        break

    c_print('Finished recieving')
    return out.decode("utf-8")

  def reply_info(self):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    req = {
      'engine':'CLI',
      'agent':'Test Agent',
      'machine_time':current_time,
      'path':self.url,
      'region':'NL/EU'
    }
    req = pickle.dumps(req)
    req = bytes(f"{len(req):<{self.HEADERSIZE}}", 'utf-8')+req
    self.s.send(req)
    
  def connect(self,a):
    a = a.strip()
    print('[CLIENT]','establishing connection to',a,str(self.port))
    try:
      self.s.connect((a,self.port))
    except Exception as e:
      return (1,f'Failed to establish a connection. Error: {e}')
    out = b""
    new = True
    leng = 0
    print('Captured:')
    while True:
      msg = self.s.recv(8)

      if new:
        leng = msg.decode("utf-8").replace('"','').strip()
        leng = int(leng[:self.HEADERSIZE])
        print('Header:',leng)
        new = False

      out += msg
      sys.stdout.write('\r'+str(len(out)-self.HEADERSIZE)+' out of '+str(leng))
      sys.stdout.flush() 
      if len(out)-self.HEADERSIZE == leng:
        print('\nDone!')
        break

    c_print('Finished recieving')
    return response(self.HEADERSIZE,out)
  
## Connect and wait for server details
#c = client(port=2020)
#
## Recieved server details
#r = c.connect(socket.gethostname())
#print(json.dumps(r.json,sort_keys=True, indent=4))
##input('sleeping...')
#
## Send back response
#c.reply_info()
#print('Sent machine info!')
#print('sleeping... Waiting for page info...')
#
#page = c.recieve_page()
#print("Page length:",len(page))
##print(page)
#
#with open("pain.html",'w+') as f:
#  f.write(page)
#
## Open result!
#os.system("poetry run python engine.py")