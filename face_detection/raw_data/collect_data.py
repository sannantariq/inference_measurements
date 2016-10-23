import os

def read_data(file):
	with open(file) as f:
		raw = f.readlines();
	return raw;

files = filter(lambda x: 'res-V-time' in x[:len('res-V-time')], os.listdir("./"));
print files
# sys.exit()
data = map(lambda x: read_data(x), files);
data = map(lambda doc: map(lambda line: line.rstrip().split('\t'), doc), data);
data_dict = {};
for doc in data:
	for [k, v] in doc:
		res = data_dict.get(k, []);
		res.append(v);
		data_dict[k] = res;


OUT_FILE = 'output_res-V-time_feat-1.txt';

output_list = data_dict.items();
output_list = map(lambda (k, v): (int(k), v), output_list);
output_list.sort();
with open(OUT_FILE, 'w') as f:
	f.write('%s\t%s\t%s\t%s\n' % ('Size(pixels)', 'piX1', 'ltX1', 'piX2'));
	for (k, v) in output_list:
		f.write('%s\t%s\n' % (k, '\t'.join(v)));

