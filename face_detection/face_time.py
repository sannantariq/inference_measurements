import numpy as np
import cv2
import timeit
import os


IMAGE_DIR = "../../face_examples/resolution/";

def get_key(x):
	_, i = x;
	r, _ = i;
	return r;

def load_images():
	img_list = [];
	dirs = os.listdir(IMAGE_DIR);
	img_list = filter(lambda x: 'face-' in x, dirs);
	img_list = map(lambda x: (x, x.split('-')[1].split('.')[0].split('x')), img_list);
	img_list = map(lambda (x, y): (x, (int(y[0]), int(y[1]))), img_list);
	img_list.sort(key = get_key);
	return img_list;

def setup_images():
	face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml');
	img_list = map(lambda (f, res): (cv2.imread("%s%s" % (IMAGE_DIR, f)), res), load_images());
	img_list = map(lambda (f, res): (cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), res), img_list);

	N = 1;
	times = [];
	for (img, (w, h)) in img_list:
		t = timeit.Timer(lambda : detect_face(img, face_cascade), "print 'setup'");
		times.append(t.timeit(N)/N);


	times = zip(times, map(lambda (x, res): res, img_list));
	times = map(lambda (x, (y, z)): (x, y * z), times);

	# print times;

	with open('plot_faces_res_pi.txt', 'w') as f:
		# f.write('Time(s)\tNo. of Pixels\n');
		f.writelines(map(lambda (x, y): "%s\t%s\n" % (y, x), times));









def setup():
	# global gray;
	# global face_cascade;
	face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml');

	cap = cv2.VideoCapture(0);
	width, height = 320, 240;
	cap.set(3, width);
	cap.set(4, height);

	if not cap.isOpened():
		cap.open();

	ret, frame = cap.read();

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);

	cap.release();

	return (gray, face_cascade);

def detect_face(matrix, cascade):
	# global face_cascade
	# global gray
	# face_cascade.detectMultiScale(gray, 1.3, 5);
	return cascade.detectMultiScale(matrix, 1.3, 5);

def calculate_time():
	matrix, cascade = setup();
	t = timeit.Timer(lambda : detect_face(matrix, cascade), "print 'setup'")
	print t.timeit(20);
	# detect_face(matrix, cascade);

setup_images()


# t = timeit.Timer(work, '');

# print t.timeit(20);
	
# calculate_time()

# face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml');

# cap = cv2.VideoCapture(0);

# if not cap.isOpened():
# 	cap.open();

# N = 1;
# detected = 0;
# for i in range(N):
# 	ret, frame = cap.read();

# 	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);

# 	timeit
# 	# faces = detect_face(gray, face_cascade);

# 	# detected += len(faces);

# 	# for (x, y, w, h) in faces:
# 	# 	cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2);

# 	# cv2.imshow('frame', frame);
# cap.release();
# cv2.destroyAllWindows()
# print "Percentage Detection = %3f" % (detected * 1.0 / N)
