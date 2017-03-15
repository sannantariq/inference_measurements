import os, argparse, sys

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
        # print self.filename
        # print "-"*5
        with open(self.filename) as f:
            raw = f.readlines();
        
        raw = map(lambda x: x.strip(), raw)
        raw = map(lambda x : x.split('\t'), raw)
        
        raw = [(x, y) for (x, _, y) in raw]
        # try:
        #     raw = [(x, y) for (x, _, y) in raw]
        # except:
        #     print raw, self.filename;
        #     sys.exit()
        self.data = raw;

    def deviceString(self):
        s = '';
        return ' + '.join(map(lambda (k, v): '%sX%s' % (k, v), self.devices.items()));

def main():
    parser = argparse.ArgumentParser();
    parser.add_argument("-p", "--port",
        help = "Port to serve on (Default is 50000)",
        type = int,
        default = 50000);

    args = parser.parse_args();
    
    server = Communicator(args.port, []);
    server.listen();

def parseFile(self, filename):
    with open(filename) as f:
        raw = f.readlines();

    raw = map(lambda x: x.strip(), raw)
    raw = map(lambda x : x.split('\t'), raw)
    raw = [(x, y) for (x, _, y) in raw]
    return raw;


def compile(dir_list, exp_name, features):
    dir_list = filter(lambda x: x.exp_name == exp_name, dir_list);
    dir_list = filter(lambda x: x.features == features, dir_list);
    map(lambda x: x.parseFile(), dir_list);
    data = {};
    for e in dir_list:
        for (x, y) in e.data:
            prev = data.get(x, []);
            prev.append((e.deviceString(), y));
            data[x] = prev;

    data = dict(map(lambda (k, v): (k, dict(v)), data.items()));
    return data;


def createOutput(data, outfile, x_label):
    x_axis = data.keys();
    x_axis.sort();

    y_axis = [];
    map(lambda x: y_axis.extend(x.keys()), data.values());
    y_axis = list(set(y_axis));
    # print y_axis;
    write_data = [];
    top_line = [x_label] + y_axis;
    write_data.append(top_line);
    for x in x_axis:
        pre_list = [''] * len(y_axis);
        for i in range(len(y_axis)):
            pre_list[i] = data[x].get(y_axis[i], '');
        write_data.append([x] + pre_list);

    write_data = map(lambda x: ','.join(x) + '\n', write_data);
    print write_data;
    with open(outfile, 'w') as f:
        f.writelines(write_data);


PATH = '../raw_data';
OUT_PATH = "../compiled_data/"
os.chdir(PATH);

dir_list = filter(lambda x: x[-3:] == 'txt', os.listdir('./'));
# print dir_list
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


data = compile(exps, 'res-V-time', '1')
createOutput(data, '%stest_output.txt' % OUT_PATH, 'Size(MB)');
# parseFile('faces-V-time_PIDocker-2_feat-3.txt')
