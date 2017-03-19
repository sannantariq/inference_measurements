import argparse, socket, sys, select, cv2, os, pickle, time, Queue;
import numpy as np;

def load_images():
    img_list = [];
    dirs = os.listdir(IMAGE_DIR);
    img_list = filter(lambda x: 'face-' in x, dirs);
    img_list = map(lambda x: (x, os.path.getsize("%s/%s" % (IMAGE_DIR, x))), img_list);
    # img_list = map(lambda x: (x, x.split('-')[1].split('.')[0].split('x')), img_list);
    # img_list = map(lambda (x, y): (x, (int(y[0]), int(y[1]))), img_list);
    img_list.sort(key = get_key);
    return img_list;

def worker_thread(input_queue, service_socket):
   while True:
    if can_run and not input_queue.empty():
      (i, task) = input_queue.get();
      start_time = time.time();
      mysocket(service_socket).mysend(pickle.dumps(task));
      response, process_time = pickle.loads(mysocket(service_socket).myreceive());
      local_dict[i] = (time.time() - start_time, process_time);
      input_queue.task_done();
      # print i, local_dict
        
def main():
    parser = argparse.ArgumentParser();
    parser.add_argument("-p", "--port",
        help = "Port to serve on (Default is 50000)",
        type = int,
        default = 50000);

    args = parser.parse_args();
    
    server = Communicator(args.port, []);
    server.listen();
    # print args.port

def get_key(x):
    # _, i = x;
    # r, _ = i;
    # return r;
    return x[1];

def initLocalDict():
    kv_list = map(lambda x: (x, (-1, -1)), range(RUNS));
    return dict(kv_list);

def processResults(data):
    """
    Check validty of results first
    """
    for (overall, process) in data:
        if process > overall:
            print "Something not right, Overall is less than processing";
            print data
        if process < 0 or overall < 0:
            print "Something not right, time is less than 0";
            print data

    """
    Then find the average
    """
    overall, process = zip(*data);
    return map(lambda x: sum(x)/len(x), [overall, process]);

def process_data(data, feat_list):
    # start_time = time.time()
    res = {};
    # matrix = pickle.loads(data);
    matrix = data
    if 'face' in feat_list:
        res['face'] = cascade_dict['face'].detectMultiScale(matrix, 1.3, 5);
        print "Faces found:", len(res["face"]);
    for (x,y,w,h) in res['face']:
        # print "Found Face";
        roi = matrix[y:y+h, x:x+w];
        for feat in feat_list:
            if feat != 'face':
                # print "Checking for : %s" % feat
                detected_area = cascade_dict[feat].detectMultiScale(roi);
                # print "Found these many: %d" % len(detected_area);
                res[feat] = res.get(feat, [])
                res[feat].append(detected_area);


    # return pickle.dumps((res, time.time() - start_time));
    return res


cascade_dict = {'face': cv2.CascadeClassifier('../../cascades/haarcascades/haarcascade_frontalface_default.xml'),
                'eye_right': cv2.CascadeClassifier('../../cascades/haarcascades/haarcascade_mcs_righteyexml'),
                'eye_left': cv2.CascadeClassifier('../../cascades/haarcascades/haarcascade_mcs_lefteye.xml'),
                'ear_right': cv2.CascadeClassifier('../../cascades/haarcascades/haarcascade_mcs_rightear.xml'),
                'ear_left': cv2.CascadeClassifier('../../cascades/haarcascades/haarcascade_mcs_leftear.xml'),
                'nose': cv2.CascadeClassifier('../../cascades/haarcascades/haarcascade_mcs_nose.xml'),
                'mouth': cv2.CascadeClassifier('../../cascades/haarcascades/haarcascade_mcs_mouth.xml'),
                'smile': cv2.CascadeClassifier('../../cascades/haarcascades/haarcascade_smile.xml')
                }


# feat_list = ['face', 'nose', 'eye_left', 'eye_right'];
feat_list_1 = ['face'];
feat_list_2 = ['face', 'eye_right', 'eye_left', 'ear_right', 'ear_left'];
feat_list_3 = ['face', 'eye_right', 'eye_left', 'ear_right', 'ear_left', 'nose', 'mouth', 'smile'];


featureDict = {1 : feat_list_1, 2 : feat_list_2, 3 : feat_list_3};


# experiments = {
# 'exp1': ('proc-res-V-time_RPI-1_feat-1.txt', [lt_feat_1]),
# }


IMAGE_DIR = "../../../face_examples/resolution/";
OUPUT_DIR = "../raw_data/";
# EXP, service_list = experiments[sys.argv[1]], ;
RUNS = 2;
FEAT = int(sys.argv[1]);
RPI_TYPE = int(sys.argv[2]);
outfile = '%sproc-res-V-time_RPI%d-1_feat-%d.txt' % (OUPUT_DIR, RPI_TYPE, FEAT);
results = {};
curr_feat = featureDict[FEAT];

init_img_list = load_images()[:5];
img_list = map(lambda (f, res): (cv2.imread("%s%s" % (IMAGE_DIR, f)), res), init_img_list);
img_list = map(lambda (f, res): (cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), res), img_list);
# img_list = map(lambda (f, res): f, img_list);
result = []
for f, res in img_list:
    start_time = time.time();
    for i in range(RUNS):
        process_data(f, curr_feat);
    time_taken = time.time() - start_time;
    avg_time_taken = time_taken / (RUNS * 1.0);
    result.append((res, (time_taken, avg_time_taken)));


with open(outfile, 'w') as f:
    for (s, (o, p)) in result:
        f.write("%f\t%s\t%s\n" % (int(s) / (1000 * 1000.0), o , p))



