# Socket server in python using select function
 
import socket, select
import json
import sys
import time
import cv2
import pickle

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
            # print "New Chunk:%s" % chunk;
            # print chunks;
            # print "SERACHING in:%s" % last_msg;
            MSG_COMP = last_msg.find("\END", max(0, len(last_msg) - len(chunks[-1]) - 10))
        return ''.join([''.join(chunks[:-2]), last_msg[:MSG_COMP]])
        # return ''.join(chunks)


def process_data(data, feat_list):
    res = {};
    matrix = pickle.loads(data);
    if 'face' in feat_list:
        res['face'] = cascade_dict['face'].detectMultiScale(matrix, 1.3, 5);

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

    return pickle.dumps(res);



port = int(sys.argv[1]);
# print port
# sys.exit()

host = '' 
# port = 50001
backlog = 5 
size = 1024 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server = mysocket(server);
server.bind((host,port)) 
server.listen(backlog) 
input = [server,sys.stdin]

# face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml');
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_lefteye.xml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_righteyexml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_leftear.xml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_rightear.xml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_mouth.xml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_nose.xml'));
# cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_smile.xml'));

cascade_dict = {'face': cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'),
                'eye_right': cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_righteyexml'),
                'eye_left': cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_lefteye.xml'),
                'ear_right': cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_rightear.xml'),
                'ear_left': cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_leftear.xml'),
                'nose': cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_nose.xml'),
                'mouth': cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_mouth.xml'),
                'smile': cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_smile.xml')
                }

feat_list = ['face', 'nose', 'eye_left', 'eye_right'];
running = 1 
while running: 
    inputready,outputready,exceptready = select.select(input,[],[], 1) 

    for s in inputready: 

        if s == server: 
            # handle the server socket 
            client, address = server.accept() 
            input.append(client);
            print "Client Added";

        elif s == sys.stdin: 
            # handle standard input 
            junk = sys.stdin.readline() 
            running = 0 

        else: 
            # handle all other sockets 
            try:
                data = mysocket(s).myreceive();
                if data: 
                    reply = process_data(data, feat_list);
                    # print "Sending reply";
                    # print pickle.loads(reply);
                    mysocket(s).mysend(reply);
            except RuntimeError:
                s.close() 
                input.remove(s)
server.close()