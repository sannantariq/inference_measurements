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
	output, error = run_cmd("kubectl -o json describe %s" % (rs));
	if error:
		return error;
	return json.loads(output);

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
def pods_by_nodes():
	info = get_nodes();
	nodeNames = {};
	for i in range(len(info['items'])):
		nodeNames[info['items'][i]['metadata']['name']] = [];
	# print nodeNames;
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


info = get_nodes()
names = get_node_names(info);
for name in names:
	print name, node_ready(info, name)
print pods_by_nodes()
# time.sleep(30)


# print find_max_diff({'a':[1, 4, 5, 5], 'b':[2, 3], 'c': [2, 5, 6]})
# pod_dict = pods_by_nodes();

# print kill_resource('po', pod_dict['minikube'][0]);
# time.sleep(10);
# print pods_by_nodes()
# # info = get_pods()
# for i in range(len(info['items'])):
# 	print info['items'][i]['metadata']['name'], info['items'][i]['status']['conditions']

