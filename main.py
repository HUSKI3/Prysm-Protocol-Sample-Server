import os
import socket
import pickle
import time
import select
from resp import response
import sys
#

def handle_client(conn, addr):
  out = b""
  new = True
  leng = 0
  HEADERSIZE = 10
  print('Captured:')
  while True:
    msg = conn.recv(8)
    if new:
      leng = msg.decode("utf-8").replace('"','').strip()
      leng = int(leng[:HEADERSIZE])
      print('Header:',leng)
      new = False
    out += msg
    sys.stdout.write('\r'+str(len(out)-HEADERSIZE)+' out of '+str(leng))
    sys.stdout.flush() 
    if len(out)-HEADERSIZE == leng:
      print('\nDone!')
      break
  return response(HEADERSIZE,out)
#
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 2020
HEADERSIZE = 10

s.bind((host, port))

sockets_list = [s]

print("Server started at: ", host)

s.listen(5)
try:
  while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for socket in read_sockets:
      if socket == s:
        clientsocket, address = s.accept()

        print(f"Connection from {address} has been established.")

        print("Asking client for engine info...")
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        req = {
          'access_type':'ip',
          'engine_req':True,
          'agent_req':True,
          'server_time':current_time,
          'region':'NL/EU'
        }
        req = pickle.dumps(req)
        req = bytes(f"{len(req):<{HEADERSIZE}}", 'utf-8')+req
        clientsocket.send(req)
        sockets_list.append(clientsocket)

        machine = handle_client(clientsocket,address)
        print('Machine info:\n',machine.json)
        path = machine.json['path']

        # Send page!!
        try:
          with open(f'server/prysm-assets/{path}','r') as f:
            index = f.read()\
              .replace('{{hostname}}',str(host))\
              .replace('{{port}}',str(port))
          req = index
          req = bytes(f"{len(req):<{HEADERSIZE}}"+req, 'utf-8')
          clientsocket.send(req)
        except:
          print("That page doesn't exit! Ignoring")
          req = '404'
          req = bytes(f"{len(req):<{HEADERSIZE}}"+req, 'utf-8')
          clientsocket.send(req)

except Exception as e:
  del s
  print('Failed',e)