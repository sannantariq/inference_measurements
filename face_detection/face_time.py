import numpy as np
import cv2
import timeit
import os
import json
import pickle
import socket, select


IMAGE_DIR = "../../face_examples/resolution/";

def get_key(x):
	_, i = x;
	r, _ = i;
	return r;

def load_images():
	img_list = [];
	dirs = os.listdir(IMAGE_DIR);
	img_list = filter(lambda x: 'face-' in x, dirs);
	img_list = map(lambda x: (x, x.split('-')[1].split('.')[0].split('x')), img_list);
	img_list = map(lambda (x, y): (x, (int(y[0]), int(y[1]))), img_list);
	img_list.sort(key = get_key);
	return img_list;

def setup_images():
	face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml');
	img_list = map(lambda (f, res): (cv2.imread("%s%s" % (IMAGE_DIR, f)), res), load_images());
	img_list = map(lambda (f, res): (cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), res), img_list);

	N = 1;
	times = [];
	for (img, (w, h)) in img_list:
		t = timeit.Timer(lambda : detect_face(img, face_cascade), "print 'setup'");
		times.append(t.timeit(N)/N);


	times = zip(times, map(lambda (x, res): res, img_list));
	times = map(lambda (x, (y, z)): (x, y * z), times);

	# print times;

	with open('plot_faces_res_pi.txt', 'w') as f:
		# f.write('Time(s)\tNo. of Pixels\n');
		f.writelines(map(lambda (x, y): "%s\t%s\n" % (y, x), times));

def detect_face(matrix, cascade):
	# global face_cascade
	# global gray
	# face_cascade.detectMultiScale(gray, 1.3, 5);
	return cascade.detectMultiScale(matrix, 1.3, 5);

def calculate_time():
	matrix, cascade = setup();
	t = timeit.Timer(lambda : detect_face(matrix, cascade), "print 'setup'")
	print t.timeit(20);
	# detect_face(matrix, cascade);

# setup_images()
# imgs = load_images();
# img_list = map(lambda (f, res): (cv2.imread("%s%s" % (IMAGE_DIR, f)), res), load_images());
# serializ = pickle.dumps(img_list[0]);


class mysocket:
    '''demonstration class only
      - coded for clarity, not efficiency
    '''

    def __init__(self, sock=None, BUF_SIZE = 4096):
        self.BUF_SIZE = BUF_SIZE;
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
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
        print "Receiveing Things..."
        chunks = []
        MSG_COMP = -1
        last_msg = '';
        while MSG_COMP < 0:
            chunk = self.sock.recv(self.BUF_SIZE);
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            last_msg = ''.join(chunks[-2:]);
            # print "New Chunk:%s" % chunk;
            # print chunks;
            # print "SERACHING in:%s" % last_msg;
            MSG_COMP = last_msg.find("\END", max(0, len(last_msg) - len(chunks[-1]) - 10))
        return ''.join([''.join(chunks[:-2]), last_msg[:MSG_COMP]])
        # return ''.join(chunks)

def process_data(data):
    print "Received:%s" % data;


def client():
	host = '' 
	port = 50001
	backlog = 5 
	size = 1024 
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# server = mysocket(server);
	server.bind((host,port)) 
	server.listen(backlog) 
	input = [server,sys.stdin] 
	running = 1 
	client_list = []
	while running: 
	    inputready,outputready,exceptready = select.select(input,[],[], 1) 

	    for s in inputready: 

	        if s == server: 
	            # handle the server socket 
	            client, address = server.accept() 
	            input.append(client); 
	            client_list.append(client);

	        elif s == sys.stdin: 
	            # handle standard input 
	            junk = sys.stdin.readline() 
	            running = 0 

	        else: 
	            # handle all other sockets 
	            try:
	                data = mysocket(s).myreceive();
	                if data: 
	                    process_data(data);
	                    mysocket(s).mysend(data);
	            except RuntimeError:
	                s.close() 
	                input.remove(s) 

	    if len(client_list) == 1:


	server.close()

def service():
	def client():
	host = '' 
	port = 50001
	backlog = 5 
	size = 1024 
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# server = mysocket(server);
	server.bind((host,port)) 
	server.listen(backlog) 
	input = [server,sys.stdin] 
	running = 1 
	client_list = []
	while running: 
	    inputready,outputready,exceptready = select.select(input,[],[], 1) 

	    for s in inputready: 

	        if s == server: 
	            # handle the server socket 
	            client, address = server.accept() 
	            input.append(client); 
	            client_list.append(client);

	        elif s == sys.stdin: 
	            # handle standard input 
	            junk = sys.stdin.readline() 
	            running = 0 

	        else: 
	            # handle all other sockets 
	            try:
	                data = mysocket(s).myreceive();
	                if data: 
	                    process_data(data);
	                    mysocket(s).mysend(data);

	            except RuntimeError:
	                s.close() 
	                input.remove(s) 

	    if len(client_list) == 1:
	    	

	server.close()

# client()