import argparse, socket, sys, select, cv2, os, pickle;
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
    img_list = map(lambda x: (x, x.split('-')[1].split('.')[0].split('x')), img_list);
    img_list = map(lambda (x, y): (x, (int(y[0]), int(y[1]))), img_list);
    img_list.sort(key = get_key);
    return img_list;

def worker_thread(input_queue, service_socket):
	while True:
		(i, task) = input_queue.get();
		mysocket(service_socket).mysend(pickle.dumps(task));
		results[i] = pickle.loads(mysocket(service_socket).myreceive());
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
    _, i = x;
    r, _ = i;
    return r;



IMAGE_DIR = "../../face_examples/resolution/"
results = {};
service_list = [('localhost', 50000), ('localhost', 50001)];
input_queue = Queue.Queue()

img_list = map(lambda (f, res): (cv2.imread("%s%s" % (IMAGE_DIR, f)), res), load_images()[6:7]);
img_list = map(lambda (f, res): (cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), res), img_list);
img_list = map(lambda (f, res): f, img_list);

map(lambda x: input_queue.put(x), enumerate(img_list));

service_list = map(lambda x: (socket.socket(socket.AF_INET, socket.SOCK_STREAM), x), service_list);
map(lambda (x, y): x.connect(y), service_list);
service_socket_list = map(lambda (x, _): x, service_list);

for s in service_socket_list:
	worker = Thread(target = worker_thread, args = (input_queue, s, ));
	worker.setDaemon(True);
	worker.start()

input_queue.join();

print results