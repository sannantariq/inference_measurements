import os, sys

def read_data(file):
	with open(file) as f:
		raw = f.readlines();
	return (file.split('_')[1], raw);

files = filter(lambda x: 'res-V-time' in x[:len('res-V-time')], os.listdir("./"));
# print files
# sys.exit()
data = map(lambda x: read_data(x), files);
# print data
# sys.exit();
data = map(lambda (title, doc): (title, map(lambda (line): line.rstrip().split('\t'), doc)), data);
# print len(data)
# sys.exit()
data_dict = {};
for (title, doc) in data:
	data_dict[title] = dict(map(lambda x: (int(x[0]), x[1]), doc));
# print data_dict
# sys.exit()
OUT_FILE = 'test-V-time_feat-1_.txt';

# print data_dict.items()
x_axis = data_dict.items()[1][1].keys();
X_AXIS_LABEL = "Size(Pixels)";
# sys.exit()
x_axis.sort();
print x_axis
with open(OUT_FILE, 'w') as f:
	f.write("%s\t" % X_AXIS_LABEL);
	for k in data_dict.keys():
		f.write("%s\t" % (k));
	f.write("\n");
	for k in x_axis:
		f.write("%d\t" % k);
		for col in data_dict.keys():
			f.write("%s\t" % data_dict[col][k]);
		f.write("\n");




# output_list = data_dict.items();
# # output_list = map(lambda (k, v): (int(k), v), output_list);
# output_list.sort();
# with open(OUT_FILE, 'w') as f:
# 	f.write('%s\t%s\t%s\t%s\n' % ('Size(pixels)', 'piX1', 'ltX1', 'piX2'));
# 	for (k, v) in output_list:
# 		f.write('%s\t%s\n' % (k, '\t'.join(v)));

