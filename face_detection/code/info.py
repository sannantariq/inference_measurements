import os,sys,json,subprocess,time

"""
This file contains functions used to gather info
info about the cluster
"""

def run_cmd(cmd):
	process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE);
	output, error = process.communicate();
	return output, error

def get_resource(rs):
	output, error = run_cmd("kubectl -o json get %s" % (rs));
	if error:
		return error;
	# return output
	return json.loads(output);

def desc_resource(rs):
	output, error = run_cmd("kubectl describe %s" % (rs));
	if error:
		return error;
	# return json.loads(output);
	return output;

def get_pods(p='po'):
	return get_resource(p);

def get_nodes(n='nodes'):
	return get_resource(n);

def desc_pods(p='po'):
	return desc_resource(p);

def desc_nodes(n='nodes'):
	return desc_resource(n);

def kill_resource(rs, name):
	output, error = run_cmd("kubectl delete %s %s" % (rs, name));
	if error:
		return error;
	return output;

# print get_nodes()['items'][0]['metadata']
def pods_by_nodes(info = None):
	if not info:
		print "info not provided"
		info = get_nodes();
	nodeNames = {};
	for i in range(len(info['items'])):
		nodeNames[info['items'][i]['metadata']['name']] = [];
	# print nodeNames;
	# if not info:
	info = get_pods();
	for i in range(len(info['items'])):
		nodeNames[info['items'][i]['spec']['nodeName']].append(info['items'][i]['metadata']['name']);
	return nodeNames

def find_max_diff(pod_dict):
	l = pod_dict.items()
	l.sort(key=lambda (x, y): len(y));
	return l[0], l[-1];

def redistribute(pod_dict):
	low, high = find_max_diff(pod_dict);
	if low == high:
		return;
	else:
		toKill = (len(pod_dict[high]) - len(pod_dict[high])) / 2
		for i in range(toKill):
			kill_resource(pod_dict[high].pop());
		return

def node_ready(info, name):
	for node in info['items']:
		# print node['metadata']
		if node['metadata']['name'] == name:
			conds = node['status']['conditions']
			for d in conds:
				if d['type'] == 'Ready':
					return d['status']
	return 'Not Found'

def count_nodes(info):
	return len(info['items']);

def get_node_names(info):
	names = [];
	for node in info['items']:
		names.append(node['metadata']['name'])
	return names


def get_node_resource(node = ""):
	output, error = run_cmd("kubectl top nodes %s" % node);
	if error:
		return error;
	return output;

def parse_top_out(s):

	s = map(lambda x: x.strip(), s.strip().split("\n"));
	s = s[1:];
	s = map(lambda x: x.split(), s);
	result = []
	for [n, cpu, cpup, mem, memp] in s:
		name = n;
		cpu_s = int(cpu[:-1]);
		cpu_pc = int(cpup[:-1]);
		mem_s = int(mem[:-2]);
		mem_pc = int(memp[:-1]);
		# print n, int(cpu[:-1]), int(cpu[:-1])
		result.append(name, (cpu_s, cpu_pc), (mem_s, mem_pc));
	return result


def record_info(outfile, t):
	records = {};
	curr_time = time.time();
	time_elapsed = time.time() - curr_time;
	while time_elapsed < t:
		output, error = get_node_resource();

		records[time_elapsed] = {}


# def get_node_metrics():
	# output, error = run_cmd("kubectl ")

print get_node_resource();

i = 0;
N = 10;
# info = get_nodes();
print "got info";
print parse_top_out(get_node_resource())
while i < 10:
	i += 1;
	# info = get_nodes();
	# print pods_by_nodes(info);
	# for node in get_node_names(info):
	# 	if  node_ready(info, node):
	# 		print pods_by_nodes(info)[node]



# info = get_nodes()
# names = get_node_names(info);
# for name in names:
# 	print name, node_ready(info, name)
# print pods_by_nodes()
# time.sleep(30)


# print find_max_diff({'a':[1, 4, 5, 5], 'b':[2, 3], 'c': [2, 5, 6]})
# pod_dict = pods_by_nodes();

# print kill_resource('po', pod_dict['minikube'][0]);
# time.sleep(10);
# print pods_by_nodes()
# # info = get_pods()
# for i in range(len(info['items'])):
# 	print info['items'][i]['metadata']['name'], info['items'][i]['status']['conditions']

