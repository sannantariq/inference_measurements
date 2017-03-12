import os, argparse

class IllegalFileError(Exception):
	"""docstring for IllegalFileError"""
	def __init__(self):
		super(IllegalFileError, self).__init__()
	def __str__(self):
		return "File name could not be parsed"

class ExpFile(object):
	"""docstring for ExpFile"""
	def __init__(self, filename):
		self.meta = filename.split("_");
		self.filename = filename
		self.exp_name = self.meta[0];
		self.translate_dict = {
		'pi' : 'pi',
		'ed' : 'edison',
		'pidocker': 'piDocker',
		'lt' : 'Laptop',
		'pikube' : 'piKube'
		}
		self.initialize()
		

	def initialize(self):
		self.features = self.meta[-1][:-4].split('-')[1]
		self.devices = map(lambda x: x.split('-'), self.meta[1:-1]);
		self.devices = {self.translate_dict[k.lower()]:v for [k, v] in self.devices}

	def __str__(self):
		return "(%s-features:%s | %s)" % (self.exp_name, self.features, repr(self.devices))

	def parseFile(self):
	with open(self.filename) as f:
		raw = f.readlines();

	raw = map(lambda x: x.strip(), raw)
	raw = map(lambda x : x.split('\t'), raw)
	raw = [(x, y) for (x, _, y) in raw]
	return raw

def main():
    parser = argparse.ArgumentParser();
    parser.add_argument("-p", "--port",
        help = "Port to serve on (Default is 50000)",
        type = int,
        default = 50000);

    args = parser.parse_args();
    
    server = Communicator(args.port, []);
    server.listen();

def parseFile(filename):
	with open(filename) as f:
		raw = f.readlines();

	raw = map(lambda x: x.strip(), raw)
	raw = map(lambda x : x.split('\t'), raw)
	raw = [(x, y) for (x, _, y) in raw]
	self.data = raw;


def compile(dir_list, exp_name):
	dir_list = filter(lambda x: x.exp_name == exp_name, dir_list);
	map(lambda x: x.parseFile(), dir_list);
	data = {};
	for 

	# dir_list = map(lambda x: ExpFile(x), dir_list)

	# print map(str,dir_list)


PATH = '../raw_data';
os.chdir(PATH);

dir_list = filter(lambda x: x[-3:] == 'txt', os.listdir('./'));
print dir_list
# ExpFile('faces-V-time_PI-2_feat-3.txt')e
# dir_list = map(lambda x: x.split('_'), dir_list)
exps = []
for f in dir_list:
	try:
		e = ExpFile(f);
		exps.append(e);
	except:
		pass;

# print map(str, exps);


# compile(exps, 'res-V-time')

parseFile('faces-V-time_PIDocker-2_feat-3.txt')