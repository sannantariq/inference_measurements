import argparse, socket, sys, select
import Queue as Q
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
        chunks = [];
        comp_msgs = [];
        while len(comp_msgs) == 0:
        	chunk = self.sock.recv(self.BUF_SIZE);
            if chunk == '':
            	if len(chunks) == 0:
            		return 0;
                raise RuntimeError("socket connection broken")

            chunks.append(chunk);
            last_msg = ''.join(chunks[-2:]);
            if 
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
        # return ''.join(chunks)

class Client(object):
	"""A single client in my communicator"""
	def __init__(self, sock, addr):
		super(Client, self).__init__()
		self.sock = sock;
		self.addr = addr;

def print_err(tag, msg):
	print "Error >> [%s] : %s" % (tag, msg);

class Communicator(object):
	"""This class specifies the communication occurring in this program"""
	def __init__(self, port, service_list, host = '', backlog = 5):
		super(Communicator, self).__init__()
		self.service_list = service_list;
		self.backlog = 5;
		self.listen_socket = None;
		self.addr = (host, port);
		self.running = 0;
		self.timeout = 0;
		self.client_dict = {};
		self.commands = {"exit" : self.stopRunning};

	def listen(self):
		self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		self.listen_socket.bind(self.addr);
		self.listen_socket.listen(self.backlog)
		self.listen_socket.setblocking(0);
		self.running = 1;
		self.input_socks = [self.listen_socket, sys.stdin];

		while self.running:
			inputready,outputready,exceptready = select.select(self.input_socks,[],[], 
				self.timeout);

			for s in inputready:

				if s == self.listen_socket:
					client, address = self.listen_socket.accept();
					self.client_dict[client] = Client(client, address);
					self.input_socks.append(client);

				elif s == sys.stdin:
					cmd = sys.stdin.readline();
					func = self.commands.get(cmd.lower().rstrip(), -1);
					if func != -1:
						func();

				else:
					client = self.client_dict.get(s, None);
					if client:
						try:
							data = client.myReceive();
							if data == 0:
								s.close();
								self.removeClient(s);
						except socket.error:
							print_err('Communicator', 'Socket Error raised');


	def removeClient(self, sock):
		if not self.client_dict.pop(sock):
			print_err('Communicator', 'Removing client that does not exist');

		if not self.input_socks.pop(self.input_socks.index(sock)):
			print_err('Communicator', 'Removing socket that does not exist');

	def stopRunning(self):
		self.running = 0;







		
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
	






main()