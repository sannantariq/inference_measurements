# Socket server in python using select function
 
import socket, select
import json
import sys
import time
import pickle
import cv2
import os
import numpy as np

IMAGE_DIR = "../../face_examples/faces/";

class mysocket:
    '''demonstration class only
      - coded for clarity, not efficiency
    '''

    def __init__(self, sock=None, BUF_SIZE = 8192):
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
        # print "Receiving Things..."
        chunks = []
        MSG_COMP = -1
        last_msg = '';
        while MSG_COMP < 0:
            chunk = self.sock.recv(self.BUF_SIZE);
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            last_msg = ''.join(chunks[-2:]);

            MSG_COMP = last_msg.find("\END", max(0, len(last_msg) - len(chunks[-1]) - 10))
        return ''.join([''.join(chunks[:-2]), last_msg[:MSG_COMP]])
        # return ''.join(chunks)

def process_data(data):
    print "Received:%s" % data;

def connect_to_services(service_list):
    connected_service = [];
    for service in service_list:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        try:
            s.connect(service);
            connected_service.append(s);
        except:
            print "Could not connect"
    return connected_service;

def send_tasks(connected_service):
    task_num = 2
    frames = range(task_num);
    tasks_sent = 0;
    img_list = load_images();
    print len(img_list)
    img = img_list[4];
    # print img
    img = cv2.imread("%s%s" % (IMAGE_DIR, img[0]));
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY);
    # print img
    # task_list = map(lambda x: (x, img), frames);
    task_list = np.hsplit(img, task_num);
    task_list = zip(frames, task_list);
    start_time = time.time();
    # print start_time;
    for (i, img) in task_list:
        mysocket(connected_service[i % len(connected_service)]).mysend(pickle.dumps(img));
        tasks_sent +=1;
    return (start_time, tasks_sent);

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

    print times;

    with open('plot_2-pis_res.txt', 'w') as f:
        # f.write('Time(s)\tNo. of Pixels\n');
        f.writelines(map(lambda (x, y): "%s\t%s\n" % (y, x), times));


# service_list = [('localhost', 50000), ('localhost', 50001)];
rpi_master_addr = ('172.20.64.128', 50000);
rpi_worker_0 = ('172.20.64.77', 50000);
service_list = [rpi_master_addr, rpi_worker_0];
host = '' 
port = 40000
backlog = 5
# size = 1024 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server = mysocket(server);
server.bind((host,port))
server.listen(backlog)
input = [server,sys.stdin]
running = 1
connected_service = [];
results = []
tasks_sent = 0;
time_taken = 0;
# start_time = time.clock();
while running:
    # print "Waiting for activity..."
    inputready,outputready,exceptready = select.select(input,[],[], 1)

    for s in inputready: 

        if s == server: 
            # handle the server socket 
            client, address = server.accept()
            input.append(client);

        elif s == sys.stdin:
            # handle standard input 
            cmd = sys.stdin.readline()
            if 'connect' in cmd:
                connected_service = connect_to_services(service_list);
                input.extend(connected_service);
            elif 'work' in cmd:
                start_time, tasks_sent = send_tasks(connected_service);
            else:
                running = 0;
            # running = 0
        else:
            # handle all other sockets 
            try:
                data = mysocket(s).myreceive();
                # print "Received data:"
                # print data
                results.append(data);
                # print results;
                if len(results) == tasks_sent:
                    running = 0;
                    time_taken = time.time() - start_time;
                    print "Total_time", time_taken

            except RuntimeError:
                s.close()
                input.remove(s)

print "Time Taken:", time_taken/2.0
[s.close() for s in connected_service]
server.close()

results = map(lambda x: pickle.loads(x), results);
print results
# [print r for r in results];