import argparse, socket, sys, select, cv2, os, pickle, time;
import Queue;
from threading import Thread;

"""

-	Create a queue with all the tasks
-	Create a thread for each service
-	The thread consumes tasks from
	the shared queue
-	Each thread itself is sequential
-	The service itself is probably
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

            MSG_COMP = last_msg.find("\END", max(0, len(last_msg) - 
            	len(chunks[-1]) - 10))
            
        return ''.join([''.join(chunks[:-2]), last_msg[:MSG_COMP]])


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


"""
Experiment Configuration
"""
IMAGE_DIR = "../../../face_examples/resolution/";
OUPUT_DIR = "../raw_data/";
EXP = "ResVsTime-LT-1.txt";
RUNS = 3;




"""
Initialization of the experiment
"""
outfile = "%s%s" % (OUPUT_DIR, EXP);
results = {};
service_list = [('localhost', 50000), ('localhost', 50001)];
input_queue = Queue.Queue()


"""
Actual Experiment
"""

init_img_list = load_images()[:3];
img_list = map(lambda (f, res): (cv2.imread("%s%s" % (IMAGE_DIR, f)), res), init_img_list);
img_list = map(lambda (f, res): (cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), res), img_list);
img_list = map(lambda (f, res): f, img_list);

service_list = map(lambda x: (socket.socket(socket.AF_INET, socket.SOCK_STREAM), x), service_list);
map(lambda (x, y): x.connect(y), service_list);
service_socket_list = map(lambda (x, _): x, service_list);

map(lambda x: input_queue.put(x), enumerate(img_list));

local_dict = None;
task_queue = Queue.Queue();
can_run = False;
worker_threads = map(lambda s: Thread(target = worker_thread, args = (task_queue, s, )), service_socket_list);
map(lambda x: x.setDaemon(True), worker_threads);
map(lambda x: x.start(), worker_threads);

while not input_queue.empty():
    (i, task) = input_queue.get();
    map(lambda x: task_queue.put((x, task)), range(RUNS));
    local_dict = initLocalDict();
    can_run = True;
    task_queue.join();
    can_run = False;
    results[i] = processResults(local_dict.values());

final = enumerate(map(lambda (_, s): s, init_img_list));
final = map(lambda (i, size): (size, (results[i][0], results[i][1])), final);
print final






# input_queue.join();

# print results

# print load_images()