import numpy as np
import cv2
import timeit
import os


IMAGE_DIR = "./face_examples/resolution/";

def split_list(data):
	res = [];
	temp = [];
	res.append([])
	for d in data:
		temp.append(d);
		res.append(temp[:]);
		# print res
	return res

def get_key(x):
	_, i = x;
	r, _ = i;
	return r;

def load_images():
	img_list = [];
	dirs = os.listdir(IMAGE_DIR);
	img_list = filter(lambda x: 'face-1024' in x, dirs);
	img_list = map(lambda x: (x, x.split('-')[1].split('.')[0].split('x')), img_list);
	img_list = map(lambda (x, y): (x, (int(y[0]), int(y[1]))), img_list);
	img_list.sort(key = get_key);
	# print img_list
	return img_list;

def setup_images():
	cascade_list = [];
	face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml');
	cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_lefteye.xml'));
	cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_righteyexml'));
	cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_leftear.xml'));
	cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_rightear.xml'));
	cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_mouth.xml'));
	cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_nose.xml'));
	cascade_list.append(cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_smile.xml'));
	# eye_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_eye.xml');
	feat_list = split_list(cascade_list);
	img_list = map(lambda (f, res): cv2.imread("%s%s" % (IMAGE_DIR, f)), load_images());
	img_list = map(lambda (f): cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), img_list);
	myimg = img_list[0];
	img_list = map(lambda (x): (myimg, x), feat_list)
	# print img_list
	# sys.exit()

	N = 10;
	times = [];
	for (img, l) in img_list:
		t = timeit.Timer(lambda : detect_face(img, face_cascade, l), "print 'setup'");
		times.append(t.timeit(N)/N);

	# print times;
	# return;


	times = zip(times, map(lambda (x): len(x), feat_list));
	# times = map(lambda (x, (y, z)): (x, y * z), times);

	print times;

	with open('plot_multi_feat.txt', 'w') as f:
		# f.write('Time(s)\tNo. of Pixels\n');
		f.writelines(map(lambda (x, y): "%s\t%s\n" % (y, x), times));

def detect_face(matrix, cascade, cascade_list):
	# global face_cascade
	# global gray
	# face_cascade.detectMultiScale(gray, 1.3, 5);
	res = []
	faces = cascade.detectMultiScale(matrix, 1.3, 5);
	res.append(faces);
	for (x,y,w,h) in faces:
		roi = matrix[y:y+h, x:x+w];
		for extra_cascade in cascade_list:
			# print "detecting extra"
			res.append(extra_cascade.detectMultiScale(roi));
		# print len(eyes);
	# print len(f);
	return res;

# print split_list(range(5));
# print load_images()
setup_images()