import numpy as np
import cv2
import timeit
import os


IMAGE_DIR = "./face_examples/resolution/";

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
	eye_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_eye.xml');
	img_list = map(lambda (f, res): (cv2.imread("%s%s" % (IMAGE_DIR, f)), res), load_images());
	img_list = map(lambda (f, res): (cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), res), img_list);

	N = 10;
	times = [];
	for (img, (w, h)) in img_list:
		t = timeit.Timer(lambda : detect_face(img, face_cascade, eye_cascade), "print 'setup'");
		times.append(t.timeit(N)/N);


	times = zip(times, map(lambda (x, res): res, img_list));
	times = map(lambda (x, (y, z)): (x, y * z), times);

	# print times;

	with open('plot_multi_res_with_eyes.txt', 'w') as f:
		# f.write('Time(s)\tNo. of Pixels\n');
		f.writelines(map(lambda (x, y): "%s\t%s\n" % (y, x), times));

def detect_face(matrix, cascade, eye_cascade):
	# global face_cascade
	# global gray
	# face_cascade.detectMultiScale(gray, 1.3, 5);
	faces = cascade.detectMultiScale(matrix, 1.3, 5);
	for (x,y,w,h) in faces:
		roi = matrix[y:y+h, x:x+w];
		eyes = eye_cascade.detectMultiScale(roi);
		# print len(eyes);
	# print len(f);
	return faces;

setup_images()
