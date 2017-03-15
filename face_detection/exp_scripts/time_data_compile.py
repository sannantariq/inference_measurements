import os, sys, argparse, subprocess

def main():
    parser = argparse.ArgumentParser();
    parser.add_argument("-f", "--file",
        help = "time-series file to compile",
        type = str);

    parser.add_argument("-c",
    	help = "compile all cumulative data",
    	action = "store_true");

    args = parser.parse_args();

    if args.c:
    	compile_all();
    else:

	    
	    
	    c_frames, t_frames = compile_data(args.file);
	    write_data(c_frames, 1);
	    write_data(t_frames, 2)

def compile_all():
	PATH = "../raw_data/"
	dir_list = filter(lambda x: "ot-custom" in x, os.listdir(PATH));
	dir_list.sort();
	data = [];
	for d in dir_list:
		with open("%s%s" % (PATH, d)) as f:
			raw = f.readlines();
		raw = raw[raw.index("\n") + 1:]
		raw = map(lambda (x, y): int(y), map(lambda l: l.strip().split(), raw))
		data.append(raw)

	scenarios = map(lambda x: 'Scenario ' + x.split("_")[0].split('-')[-1], dir_list);

	print len(data), len(scenarios), len(data[0]);
	with open("compiled_cumulative.txt", "w") as f:
		f.write(','.join(['Time(seconds)'] + scenarios));
		f.write("\n");
		for i in range(len(data[0])):
			line = [];
			line.append("%d" % i);
			for j in range(len(data)):
				if i < len(data[j]):
					line.append("%d" % data[j][i]);
				else:
					line.append('');
			f.write(','.join(line) + "\n");


def compile_data(filename):
	with open(filename) as f:
		raw = f.readlines();

	raw = raw[raw.index("\n") + 1:]
	raw = map(lambda s: s.split(), map(lambda s: s.strip(), raw))

	frames = map(lambda (i, (_, y)): (i, y), enumerate(raw))
	cumulative_frames = frames[:];

	frames = map(lambda (x, y): (int(x), int(y)), frames);
	shifted_frames = map(lambda (x, y): y, [(0, 0)] + frames[:-1]);
	
	time_frames = map(lambda (p, (x, y)): (x, y-p), zip(shifted_frames, frames));
	return cumulative_frames, time_frames

def write_data(data, form):
	if form == 1:
		with open(TEMP_CUMU_FILE, 'w') as f:
			f.write("Time(seconds),Total Frames Processed\n");
			for (x, y) in data:
				f.write("%d,%d\n" % (int(x), int(y)));
		# subprocess.call(['gnuplot', ''])

	elif form == 2:
		with open(TEMP_TS_FILE, 'w') as f:
			f.write("Time(seconds),Frames Per Second\n");
			for (x, y) in data:
				f.write("%d,%d\n" % (x, y));

	
TEMP_CUMU_FILE = "cumulative.txt";
TEMP_TS_FILE = "timeseries.txt";

main()