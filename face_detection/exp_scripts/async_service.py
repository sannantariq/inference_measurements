# Socket server in python using select function
 
import socket, select
import json
import sys
import time
import cv2
import pickle
import Queue
import os
from threading import Thread
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
        self.buffer = '';

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
        chunk = self.buffer + self.sock.recv(self.BUF_SIZE);
        # print chunk
        chunks = chunk.split("\END\n");
        # print chunks
        self.buffer = chunks[-1];
        chunks = chunks[:-1];
        # print chunks
        return chunks;

        # chunks = []
        # MSG_COMP = -1
        # last_msg = '';
        # while MSG_COMP < 0:
        #     chunk = self.sock.recv(self.BUF_SIZE);
        #     if chunk == '':
        #         raise RuntimeError("socket connection broken")
        #     chunks.append(chunk)
        #     last_msg = ''.join(chunks[-2:]);
        #     # print "New Chunk:%s" % chunk;
        #     # print chunks;
        #     # print "SERACHING in:%s" % last_msg;
        #     MSG_COMP = last_msg.find("\END", max(0, len(last_msg) - len(chunks[-1]) - 10))
        # return ''.join([''.join(chunks[:-2]), last_msg[:MSG_COMP]])
        # return ''.join(chunks)


def process_data(data, feat_list):
    print "processing";
    start_time = time.time()
    res = {};
    matrix = pickle.loads(data);
    if 'face' in feat_list:
        res['face'] = cascade_dict['face'].detectMultiScale(matrix, 1.3, 5);
        print "Faces found:", len(res["face"]);
    for (x,y,w,h) in res['face']:
        # print "Found Face";
        roi = matrix[y:y+h, x:x+w];
        for feat in feat_list:
            if feat != 'face':
                # print "Checking for : %s" % feat
                detected_area = cascade_dict[feat].detectMultiScale(roi);
                # print "Found these many: %d" % len(detected_area);
                res[feat] = res.get(feat, [])
                res[feat].append(detected_area);


    return pickle.dumps((res, time.time() - start_time));

def consume_thread(task_queue, current_feat):
    while True:
        if not task_queue.empty():
            print "Processing task in thread"
            data, client = task_queue.get();
            reply = process_data(data, current_feat)
            # reply = MY_NAME + " says: " + data;
            mysocket(client).mysend(pickle.dumps(reply));
            task_queue.task_done();
            # print "Reply sent";

if len(sys.argv) < 2:
    print "Usage: ./service.py <featureSet> [port]"
    sys.exit();

try:
    featureSet = int(sys.argv[1]);
    if featureSet not in [1, 2, 3]:
        print "<featureSet> must be integer from {1, 2, 3}"
        sys.exit();
except ValueError:
    print "<featureSet> must be integer from {1, 2, 3}"
    sys.exit();

DEF_PORT = 50000
if len(sys.argv) > 2:
    try:
        port = int(sys.argv[2]);
    except ValueError:
        port = DEF_PORT;
else:
    port = DEF_PORT;

PATH_1 = "/data/src/inference_measurements/cascades/haarcascades"
PATH_2 = "../../cascades/haarcascades/"
if os.path.exists(PATH_1):
    PATH = PATH_1;
elif os.path.exists(PATH_2):
    PATH = PATH_2;
else:
    print "Error: Cascades not found!. Exiting..."
    sys.exit();

# print port
# sys.exit()

MY_NAME = str(socket.getfqdn());
host = '' 
# port = 50001
backlog = 5 
size = 1024 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server = mysocket(server);
server.bind((host,port)) 
server.listen(backlog) 
input = [server]



# face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml');
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_lefteye.xml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_righteyexml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_leftear.xml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_rightear.xml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_mouth.xml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_nose.xml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_smile.xml'));



cascade_dict = {'face': cv2.CascadeClassifier('%s/haarcascade_frontalface_default.xml' % (PATH)),
                'eye_right': cv2.CascadeClassifier('%s/haarcascade_mcs_righteyexml' % (PATH)),
                'eye_left': cv2.CascadeClassifier('%s/haarcascade_mcs_lefteye.xml' % (PATH)),
                'ear_right': cv2.CascadeClassifier('%s/haarcascade_mcs_rightear.xml' % (PATH)),
                'ear_left': cv2.CascadeClassifier('%s/haarcascade_mcs_leftear.xml' % (PATH)),
                'nose': cv2.CascadeClassifier('%s/haarcascade_mcs_nose.xml' % (PATH)),
                'mouth': cv2.CascadeClassifier('%s/haarcascade_mcs_mouth.xml' % (PATH)),
                'smile': cv2.CascadeClassifier('%s/haarcascade_smile.xml' % (PATH))
                }


# feat_list = ['face', 'nose', 'eye_left', 'eye_right'];

feat_list_1 = ['face'];
feat_list_2 = ['face', 'eye_right', 'eye_left', 'ear_right', 'ear_left'];
feat_list_3 = ['face', 'eye_right', 'eye_left', 'ear_right', 'ear_left', 'nose', 'mouth', 'smile'];
featureDict = {1 : feat_list_1, 2 : feat_list_2, 3 : feat_list_3};

current_feat = featureDict[featureSet]

task_queue = Queue.Queue();
con_thread = Thread(target = consume_thread, args = (task_queue, current_feat, ));
con_thread.setDaemon(True);
con_thread.start();

running = 1
print "Providing service at port %d for featureSet:" % port, featureSet
clients = {};
while running: 
    inputready,outputready,exceptready = select.select(input,[],[], 0.1)

    for s in inputready: 

        if s == server: 
            # handle the server socket 
            client, address = server.accept() 
            input.append(client);
            clients[client] = mysocket(client);
            print "New Client Added";


        else: 
            # handle all other sockets 
            try:
                data = clients[s].myreceive();
                # data = s.recv(100);

                if len(data) > 0:
                    # reply = process_data(data, current_feat);
                    # print "Sending reply";
                    # print pickle.loads(reply);
                    # reply = str(socket.getfqdn()) + " says: " + data;
                    # mysocket(s).mysend(reply);
                    # tasks = map(pickle.loads, data);

                    # print "Tasks Received:", tasks
                    map(lambda t : task_queue.put((t, s)), data)
                    # task_queue.put((data, s));
                elif clients[s].buffer == '':
                    s.close();
                    input.remove(s);
            except RuntimeError:
                s.close() 
                input.remove(s)
server.close()