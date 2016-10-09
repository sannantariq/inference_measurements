# Socket server in python using select function
 
import socket, select
import json
import sys
import time

class mysocket:
    '''demonstration class only
      - coded for clarity, not efficiency
    '''

    def __init__(self, sock=None, BUF_SIZE = 4096):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.BUF_SIZE = BUF_SIZE;
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        msg += "\END\n";
        MSGLEN = len(msg);
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self):
        chunks = []
        MSG_COMP = -1
        while not MSG_COMP < 0:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, self.BUF_SIZE))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            last_msg = ''.join(chunks[:-2]);
            MSG_COMP = last_msg.find("\END", len(last_msg) - len(chunks[-1]) - 4)
        ''.join(chunks)
        return ''.join(chunks)


host = '' 
port = 50000 
backlog = 5 
size = 1024 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((host,port)) 
server.listen(backlog) 
input = [server,sys.stdin] 
running = 1 
while running: 
    inputready,outputready,exceptready = select.select(input,[],[]) 

    for s in inputready: 

        if s == server: 
            # handle the server socket 
            client, address = server.accept() 
            input.append(client) 

        elif s == sys.stdin: 
            # handle standard input 
            junk = sys.stdin.readline() 
            running = 0 

        else: 
            # handle all other sockets 
            data = s.recv(size) 
            if data: 
                process_data(data);
            else: 
                s.close() 
                input.remove(s) 
server.close()