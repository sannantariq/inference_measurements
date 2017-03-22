import argparse, socket, sys, select, cv2, os, pickle, time, Queue;
import numpy as np;
from threading import Thread;

"""

-   Create a queue with all the tasks
-   Create a thread for each service
-   The thread consumes tasks from
    the shared queue
-   Each thread itself is sequential
-   The service itself is probably
    I/O multiplexed

"""

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


        # while 
        # MSG_COMP = -1
        # last_msg = '';
        # while MSG_COMP < 0:
        #     chunk = self.sock.recv(self.BUF_SIZE);
        #     if chunk == '':
        #         raise RuntimeError("socket connection broken")
        #     chunks.append(chunk)
        #     last_msg = ''.join(chunks[-2:]);

        #     MSG_COMP = last_msg.find("\END", max(0, len(last_msg) - 
        #         len(chunks[-1]) - 10))
            
        # return ''.join([''.join(chunks[:-2]), last_msg[:MSG_COMP]])


def load_images():
    img_list = [];
    dirs = os.listdir(IMAGE_DIR);
    img_list = filter(lambda x: 'face-' in x, dirs);
    img_list = map(lambda x: (x, os.path.getsize("%s/%s" % (IMAGE_DIR, x))), img_list);
    # img_list = map(lambda x: (x, x.split('-')[1].split('.')[0].split('x')), img_list);
    # img_list = map(lambda (x, y): (x, (int(y[0]), int(y[1]))), img_list);
    img_list.sort(key = get_key);
    return img_list;

def worker_thread(input_queue, service_socket):
   while True:
    if can_run and not input_queue.empty():
      (i, task) = input_queue.get();
      start_time = time.time();
      mysocket(service_socket).mysend(pickle.dumps(task));
      response, process_time = pickle.loads(mysocket(service_socket).myreceive());
      local_dict[i] = (time.time() - start_time, process_time);
      input_queue.task_done();
      # print i, local_dict
        
def main():
    parser = argparse.ArgumentParser();
    parser.add_argument("-p", "--port",
        help = "Port to serve on (Default is 50000)",
        type = int,
        default = 50000);

    args = parser.parse_args();
    
    server = Communicator(args.port, []);
    server.listen();
    # print args.port

def get_key(x):
    # _, i = x;
    # r, _ = i;
    # return r;
    return x[1];

def initLocalDict():
    kv_list = map(lambda x: (x, (-1, -1)), range(RUNS));
    return dict(kv_list);

def processResults(data):
    """
    Check validty of results first
    """
    for (overall, process) in data:
        if process > overall:
            print "Something not right, Overall is less than processing";
            print data
        if process < 0 or overall < 0:
            print "Something not right, time is less than 0";
            print data

    """
    Then find the average
    """
    overall, process = zip(*data);
    return map(lambda x: sum(x)/len(x), [overall, process]);


def splitFrame(frame, min_splits):
    splits = [frame];
    # print len(splits), len(splits[0]), len(splits[0][0]);
    while len(splits) < min_splits:
        h, w = splits[0].shape;
        if h > w:
            temp = map(lambda x: np.array_split(x, 2, 0), splits);
        else:
            temp = map(lambda x: np.array_split(x, 2, 1), splits);
        splits = [];
        map(lambda x: splits.extend(x), temp);
        # print splits[0].shape;
        # print len(splits)
    return splits;

def generateTaskQueueSplits(task_list, service_list):
    input_queue = Queue.Queue();
    for (i, task) in enumerate(task_list):
        # splits = enumerate(splitFrame(task, len(service_list)));
        # print len(splits);
        input_queue.put((i, list(enumerate(splitFrame(task, len(service_list))))));
    return input_queue;
        


def generateTaskQueueCopies(task_list):
    input_queue = Queue.Queue();
    for (i, task) in enumerate(task_list):
        input_queue.put((i, map(lambda x: (x, task), range(RUNS))));
    return input_queue;

def generateQueues(task_list):
    input_queue = Queue.Queue();
    for (i, task) in enumerate(task_list):
        iQueue = Queue.Queue();
        for _ in range(RUNS):
            iQueue.put(task);
        input_queue.put((i, iQueue));
    return input_queue;

def send_thread(img_queue, service_addr, service_socket):
    while True:
        if not img_queue.empty():
            # print "Sending task..."
            try:
                mysocket(service_socket).mysend(pickle.dumps(img_queue.get()));
                img_queue.task_done();
            except socket.error as err:
                # service_socket.close();
                print "Error while sending!!";
                print err
                break;
                # service_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # c = 1;
                # while c != 0:
                #     c = service_socket.connect_ex(service_addr);
                #     print c
                #     time.sleep(1);
                # pass
            if img_queue.empty():
                print "Ran out of frames to send...";


def recv_thread(out_queue, service_addr, service_socket, service):
    while True:
        # print "Receiveing..."
        try:
            response = map(pickle.loads, service.myreceive());
            if len(response) > 0:
                # print "Response received:", response;
                map(out_queue.put, response);
            elif service.buffer == '':
                service_socket.close()
                break
        except socket.error as err:
            # service_socket.close();
            print "Error while receiveing!"
            print err
            break;
            # service_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
            # c = 1;
            # while c != 0:
            #     c = service_socket.connect_ex(service_addr);
            #     print c
            #     time.sleep(1);
            # service = mysocket(service_socket);
                # pass


        # out_queue.put(response);

def keep_threads_alive(service_context, img_queue, out_queue):
    while True:
        closed_threads = filter(lambda (i, x): x == False, enumerate(map(lambda (_, _z, (st, rt)): st.is_alive() and rt.is_alive(), service_context)))
        for i, t in closed_threads:
            print "Restarting Thread %d" % i;

            old_sock, y, _ = service_context[i];
            old_sock.close();
            x = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
            conn = False;
            while not conn:
                print "Attempting Connection..."
                try:
                    x.connect(y);
                    conn = True;
                except socket.error as err:
                    print "Failed with error: %s" % err;
                    time.sleep(1);
            # x.connect(y);

            st, rt = (Thread(target = send_thread, args = (img_queue, y, x, )), 
            Thread(target = recv_thread, args = (out_queue, y, x, mysocket(x))));

            service_context[i] = (x, y, (st, rt));

            st.setDaemon(True);
            rt.setDaemon(True);
            st.start();
            rt.start();





rpi1_ip = '172.20.64.55'
rpi2_ip = '172.20.64.180'


kb_ip = '10.108.225.170'

lt_feat_1 = ('localhost', 50000);
lt_feat_11 = ('localhost', 50004);
lt_feat_111 = ('localhost', 50005);
lt_feat_2 = ('localhost', 50001);
lt_feat_3 = ('localhost', 50002);

ed1_feat_1 = ('172.20.99.60', 50000);
ed1_feat_2 = ('172.20.99.60', 50001);
ed1_feat_3 = ('172.20.99.60', 50002);

ed2_feat_1 = ('172.20.96.110', 50000);
ed2_feat_2 = ('172.20.96.110', 50001);
ed2_feat_3 = ('172.20.96.110', 50002);

rpi1_feat_1 = (rpi1_ip, 50000);
rpi1_feat_2 = (rpi1_ip, 50001);
rpi1_feat_3 = (rpi1_ip, 50002);

rpi2_feat_1 = (rpi2_ip, 50000);
rpi2_feat_2 = (rpi2_ip, 50001);
rpi2_feat_3 = (rpi2_ip, 50002);

rpiDock_feat_1 = ('172.20.64.110', 50000);

rpiDock2_feat_1 = ('172.20.64.223', 8080);

rpiKb_feat_1 = (rpi1_ip, 31331);
rpiKb_feat_2 = (rpi1_ip, 32745)
rpiKb_feat_3 = (rpi1_ip, 31425)
minikube_feat_1 = ('192.168.99.100', 32584);

"""
Spec-1: No Messing Around
Spec-2: Kill container on weaker Pi
Spec-3: Kill container on stronger Pi
Spec-4: Kill weaker Pi
Spec-5: Kill stronger Pi
"""

experiments = {
0 : ('ot-test.txt', [rpiKb_feat_1], 1),
1 : ('ot-spec-1_lt-1_feat-1.txt', [lt_feat_1], 1),
2 : ('ot-spec-1_ltkube-1_feat-1.txt', [minikube_feat_1], 1),
3 : ('saturate_containers-4_piKubeRed-1_feat-1.txt', [rpiKb_feat_1], 1),
4 : ('saturate_containers-4_piKubeRed-1_feat-1.txt', [rpiKb_feat_1], 2),
5 : ('saturate_containers-4_piKubeRed-1_feat-1.txt', [rpiKb_feat_1], 3),
6 : ('saturate_containers-4_piKubeRed-1_feat-1.txt', [rpiKb_feat_1], 4),
7 : ('saturate_containers-4_piKubeRed-1_feat-1.txt', [rpiKb_feat_1], 5),
8 : ('saturate_containers-4_piKubeRed-1_feat-1.txt', [rpiKb_feat_1], 6),
9 : ('saturate_containers-4_piKubeBlue-1_feat-1.txt', [rpiKb_feat_1], 1),
10 : ('saturate_containers-4_piKubeBlue-1_feat-1.txt', [rpiKb_feat_1], 2),
11 : ('saturate_containers-4_piKubeBlue-1_feat-1.txt', [rpiKb_feat_1], 3),
12 : ('saturate_containers-4_piKubeBlue-1_feat-1.txt', [rpiKb_feat_1], 4),
13 : ('saturate_containers-4_piKubeBlue-1_feat-1.txt', [rpiKb_feat_1], 5),
14 : ('saturate_containers-4_piKubeBlue-1_feat-1.txt', [rpiKb_feat_1], 6),
}

"""
Experiment Configuration
"""

IMAGE_DIR = "../../../face_examples/resolution/";
OUPUT_DIR = "../raw_data/";
EXP, service_list, thread_count = experiments[int(sys.argv[1])];
TIME_LIMIT = 60;
# EXP, service_list = ('test_output.txt', [lt_feat_1, lt_feat_11, lt_feat_111])
RUNS = 1;
frame_copies = 500;
IMG = 0;

service_list = service_list * thread_count;




# """
# Initialization of the experiment
# """
outfile = "%s%s_threads-%d.txt" % (OUPUT_DIR, EXP[:-4], thread_count);
results = {};
# service_list = [('localhost', 50000), ('localhost', 50001)];
# service_list = [('localhost', 50000)];
# service_list = [('172.20.96.110', 50000)];
# service_list = [('172.20.99.60', 50000)];
# service_list = [('172.20.99.60', 50000), ()]


"""
Actual Experiment
"""

# IMAGE_DIR = "../../../face_examples/resolution/";

# init_img_list = load_images()[:5];
# print init_img_list
# img_list = map(lambda (f, res): (cv2.imread("%s%s" % (IMAGE_DIR, f)), res), init_img_list);
# img_list = map(lambda (f, res): (cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), res), img_list);
# print img_list
init_img, size = load_images()[IMG]
# print init_img
init_img = cv2.imread("%s%s" % (IMAGE_DIR, init_img));
# print init_img
init_img = cv2.cvtColor(init_img, cv2.COLOR_BGR2GRAY);

# sys.exit()

out_queue = Queue.Queue();
img_queue = Queue.Queue();
for i in range(frame_copies):
    img_queue.put(init_img);
    # img_queue.put("Hello World" + str(i))

# service_list = [
# lt_feat_1
# ]

# addr = lt_feat_1
# service = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
# service.connect(addr);

# worker_threads = {
# 'sender' : Thread(target = send_thread, args = (img_queue, service, )), 
# 'receiver' :Thread(target = recv_thread, args = (out_queue, service, mysocket(service)))
# }
# map(lambda x: x.setDaemon(True), worker_threads.values());
# map(lambda x: x.start(), worker_threads.values());


service_list = map(lambda x: (socket.socket(socket.AF_INET, socket.SOCK_STREAM), x), service_list);
map(lambda (x, y): x.connect(y), service_list);
service_socket_list = map(lambda (x, _): x, service_list);
service_context = map(lambda (x, y): (x, y,
    (Thread(target = send_thread, args = (img_queue, y, x, )), 
        Thread(target = recv_thread, args = (out_queue, y, x, mysocket(x), )))), service_list);
map(lambda (_, _z, (s, r)): (s.setDaemon(True), r.setDaemon(True)), service_context);
map(lambda (_, _z, (s, r)): (s.start(), r.start()), service_context);

health_thread = Thread(target = keep_threads_alive, args = (service_context, img_queue, out_queue, ))
health_thread.setDaemon(True);
health_thread.start();

start_time = time.time();

# while out_queue.qsize() <= frame_copies:
#     if out_queue.qsize() == frame_copies:
#         print "All tasks received!"
#         break;

# while not out_queue.empty():
#     print out_queue.get();

results = []
# # c_p = 0;
# s = out_queue.qsize();
# while s <= frame_copies:
#     # c = out_queue.qsize() - c_p;
#     results.append((time.time() - start_time, s));
#     time.sleep(1)
#     s = out_queue.qsize();
#     if out_queue.qsize() == frame_copies:
#         print "All tasks received!"
#         results.append((time.time() - start_time, s))
#         break;

while time.time() - start_time < TIME_LIMIT:
    s = out_queue.qsize();
    results.append((time.time() - start_time, s));
    time.sleep(1)

print results;

with open(outfile, 'w') as f:
    map(lambda i: f.write("%f %d\n" % i), results);

#############################################


# service_list = map(lambda x: (socket.socket(socket.AF_INET, socket.SOCK_STREAM), x), service_list);
# map(lambda (x, y): x.connect(y), service_list);
# service_socket_list = map(lambda (x, _): x, service_list);

# # map(lambda x: input_queue.put(x), enumerate(img_list));

# local_dict = None;
# task_queue = Queue.Queue();
# can_run = False;
# worker_threads = map(lambda s: Thread(target = worker_thread, args = (task_queue, s, )), service_socket_list);
# map(lambda x: x.setDaemon(True), worker_threads);
# map(lambda x: x.start(), worker_threads);


# while not input_queue.empty():
#     (i, task_list) = input_queue.get();
#     map(lambda x: task_queue.put(x), task_list);
#     local_dict = initLocalDict();
#     overall_time = time.time()
#     can_run = True;
#     task_queue.join();
#     overall_time = time.time() - overall_time;
#     can_run = False;
#     results[i] = processResults(local_dict.values());
#     # print i, overall_time, overall_time/RUNS
#     # results[i] = (overall_time, overall_time/RUNS)

# # print results
# print "-"*20
# # print local_dict
# # sys.exit()

# final = enumerate(map(lambda (_, s): s, init_img_list));
# final = map(lambda (i, size): (size, (results[i][0], results[i][1])), final);


# print final
# with open(outfile, 'w') as f:
#     for (s, (o, p)) in final:
#         f.write("%f\t%s\t%s\n" % (int(s) / (1000 * 1000.0), o , p))


# # while not input_queue.empty():
# #     print input_queue.get()
# # print input_queue.qsize();
# # print len(input_queue.get()[1]);

# # input_queue.join();

# # print results

# # print load_images()

#####################